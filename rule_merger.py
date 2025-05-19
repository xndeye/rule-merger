import yaml
import requests
import os
import logging
from typing import List, Dict, Optional, Literal
import re
from dataclasses import dataclass
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 添加常量定义
RULE_TYPES = {
    'classical': {'DOMAIN', 'DOMAIN-SUFFIX', 'IP-CIDR', 'IP-CIDR6'},
    'ipcidr': {'IP-CIDR', 'IP-CIDR6'},
    'domain': {'DOMAIN', 'DOMAIN-SUFFIX'}
}

DOMAIN_PATTERN = r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*$'
IPV4_CIDR_PATTERN = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
IPV6_CIDR_PATTERN = r'^([0-9a-fA-F:]+)/\d{1,3}$'

@dataclass
class RuleSource:
    """规则源配置数据类"""
    type: Literal['http', 'file']  # 使用 Literal 类型限制
    url: str = ''
    path: str = ''
    behavior: Literal['classical', 'ipcidr', 'domain'] = 'classical'

class RulesMerger:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger(__name__)
        self._transformers = {
            ('classical', 'ipcidr'): self._classical_to_ipcidr,
            ('classical', 'domain'): self._classical_to_domain,
            ('ipcidr', 'classical'): self._ipcidr_to_classical,
            ('domain', 'classical'): self._domain_to_classical
        }

    def _load_config(self, path: str) -> dict:
        """加载配置文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.error(f"配置文件不存在: {path}")
            raise
        except yaml.YAMLError as e:
            self.logger.error(f"配置文件解析失败: {e}")
            raise
    
    def _fetch_http_rules(self, url: str, format: str) -> List[str]:
        """获取在线规则"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            if format == 'yaml' or 'yaml' in content_type or url.endswith(('.yml', '.yaml')):
                data = yaml.safe_load(response.text)
                # 处理可能的 payload 嵌套
                if isinstance(data, dict) and 'payload' in data:
                    return data['payload'] or []
                return data or []
            return response.text.splitlines()
        except Exception as e:
            self.logger.error(f"获取规则失败 {url}: {str(e)}", exc_info=True)
            return []
    
    def _transform(self, rule: str, source_behavior: str, target_behavior: str) -> Optional[str]:
        """转换规则格式"""
        if not rule:
            return None
            
        if source_behavior == target_behavior:
            validators = {
                'classical': self._validate_classical_rule,
                'ipcidr': self._validate_ipcidr_rule,
                'domain': self._validate_domain_rule
            }
            validator = validators.get(source_behavior)
            if validator:
                return validator(rule)
            return rule
            
        transformer = self._transformers.get((source_behavior, target_behavior))
        if not transformer:
            return None
            
        return transformer(rule)

    def _classical_to_ipcidr(self, rule: str) -> Optional[str]:
        """将经典规则转换为IP-CIDR规则"""
        if not (rule.startswith('IP-CIDR,') or rule.startswith('IP-CIDR6,')):
            return None
        parts = rule.split(',')
        if len(parts) < 2:
            return None
        return parts[1].strip()
    
    def _classical_to_domain(self, rule: str) -> Optional[str]:
        """将经典规则转换为DOMAIN规则"""
        parts = rule.split(',')
        if len(parts) < 2:
            return None
            
        domain = parts[1].strip()
        # 验证域名格式
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*$', domain):
            return None
            
        if rule.startswith('DOMAIN,'):
            return domain
        elif rule.startswith('DOMAIN-SUFFIX,'):
            return '+.' + domain
        return None
    
    def _ipcidr_to_classical(self, rule: str) -> Optional[str]:
        """将IP-CIDR规则转换为经典规则"""
        if ':' in rule:
            return "IP-CIDR6," + rule
        return "IP-CIDR," + rule
    
    def _domain_to_classical(self, rule: str) -> Optional[str]:
        """将DOMAIN规则转换为经典规则"""
        if rule.startswith('+.'):
            suffix = rule[2:]
            if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*$', suffix):
                return None
            return f"DOMAIN-SUFFIX,{suffix}"
        
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*$', rule):
            return None
        return f"DOMAIN,{rule}"
    
    def _read_local_rules(self, path: str, format: str) -> List[str]:
        """读取本地规则"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if format == 'yaml':
                    data = yaml.safe_load(f)
                    # 处理可能的 payload 嵌套
                    if isinstance(data, dict) and 'payload' in data:
                        return data['payload'] or []
                    return data or []
                return f.read().splitlines()
        except Exception as e:
            print(f"读取本地规则失败 {path}: {str(e)}")
            return []
    
    def _clean_rule(self, rule: str) -> str:
        """清理规则中的注释内容"""
        rule = rule.strip()
        
        if rule.startswith('#'):
            return ''
        
        parts = re.split(r'\s+#', rule)
        if len(parts) > 1:
            rule = parts[0]

        return rule.strip()
    
    def _process_source(self, source: Dict, target_behavior: str) -> List[str]:
        """处理单个规则源"""
        rules = []

        format = source.get('format', 'yaml')
        if source['type'] == 'http':
            rules = self._fetch_http_rules(source['url'], format)
        elif source['type'] == 'file':
            rules = self._read_local_rules(source['path'], format)
        
        
        converted_rules = []
        source_behavior = source.get('behavior', 'classical')
        for rule in rules:
            if rule is None:
                continue
            cleaned_rule = self._clean_rule(rule)
            # logging.info(f"清理后的规则: {cleaned_rule}")
            transformed_rule = self._transform(cleaned_rule, source_behavior, target_behavior)
            if not transformed_rule:
                continue
            converted_rules.append(transformed_rule)
        
        return converted_rules
    
    def merge_rules(self) -> None:
        """合并所有规则并生成文件"""
        for config in self.config:
            if 'upstream' not in config or not config.get('path'):
                continue
            
            # 获取目标格式（整个配置文件的输出格式）
            target_behavior = config.get('behavior', 'classical')
            merged_rules = []
            
            # 处理每个上游源
            for source_name, source_config in config['upstream'].items():
                rules = self._process_source(source_config, target_behavior)
                merged_rules.extend(rules)
            
            # 去重和排序
            merged_rules = sorted(set(merged_rules))
            self._write_rules(config['path'], merged_rules)
    
    def _write_rules(self, output_path: str, rules: List[str]) -> None:
        """写入规则到文件"""
        try:
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# 规则数量: {len(rules)}\n")
                # 创建一个格式化的 YAML 字符串
                yaml_str = yaml.dump(
                    {'payload': rules}, 
                    allow_unicode=True, 
                    indent=2,  # 设置基本缩进为2
                    default_flow_style=False,  # 强制使用块样式
                    sort_keys=False
                )
                # 确保 payload 下的每个项目都有正确的缩进
                formatted_yaml = yaml_str.replace('\n-', '\n  -')
                f.write(formatted_yaml)
            
            self.logger.info(f"已生成规则文件: {output_path}, 共 {len(rules)} 条规则")
        except Exception as e:
            self.logger.error(f"写入规则文件失败: {str(e)}", exc_info=True)
            raise
    
    def _validate_classical_rule(self, rule: str) -> Optional[str]:
        """验证经典规则格式"""
        try:
            parts = rule.split(',')
            if len(parts) < 2:
                return None
                
            rule_type = parts[0]
            value = parts[1].strip()
            
            # if rule_type not in RULE_TYPES['classical']:
            #     return None
                
            if rule_type in {'DOMAIN', 'DOMAIN-SUFFIX'}:
                return rule if re.match(DOMAIN_PATTERN, value) else None
            elif rule_type == 'IP-CIDR':
                return rule if re.match(IPV4_CIDR_PATTERN, value) else None
            elif rule_type == 'IP-CIDR6':
                return rule if re.match(IPV6_CIDR_PATTERN, value) else None
        except Exception as e:
            self.logger.debug(f"规则验证失败: {rule}, 错误: {str(e)}")
            return None
        return rule

    def _validate_ipcidr_rule(self, rule: str) -> Optional[str]:
        """验证 IP-CIDR 规则格式"""
        return rule

    def _validate_domain_rule(self, rule: str) -> Optional[str]:
        """验证域名规则格式"""
        return rule

def main():
    merger = RulesMerger('config.yaml')
    merger.merge_rules()

if __name__ == '__main__':
    main()