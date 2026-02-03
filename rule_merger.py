import yaml
import subprocess
import tempfile
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

DOMAIN_PATTERN = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*$')
IPV4_CIDR_PATTERN = re.compile(r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$')
IPV6_CIDR_PATTERN = re.compile(r'^([0-9a-fA-F:]+)/\d{1,3}$')
MIHOMO_PATH = 'mihomo'


@dataclass
class RuleSource:
    """规则源配置数据类"""
    type: Literal['http', 'file']  # 使用 Literal 类型限制
    url: str = ''
    path: str = ''
    behavior: Literal['classical', 'ipcidr', 'domain'] = 'classical'
    format: Literal['text', 'yaml', 'mrs'] = 'yaml'

class RulesMerger:
    def __init__(self, config_path: str):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.mihomo_path = MIHOMO_PATH
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
    
    def _fetch_http_rules(self, url: str, rule_format: str, behavior: str = 'classical') -> List[str]:
        """获取在线规则"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            # rule_format 优先；仅当格式未明确指定时依赖 Content-Type / URL 后缀推断
            is_yaml = (rule_format == 'yaml') or (
                rule_format not in ('mrs', 'text') and
                ('yaml' in content_type or url.endswith(('.yml', '.yaml')))
            )
            if is_yaml:
                data = yaml.safe_load(response.text)
                # 处理可能的 payload 嵌套
                if isinstance(data, dict) and 'payload' in data:
                    return data['payload'] or []
                return data or []
            
            if rule_format == 'mrs':
                with tempfile.NamedTemporaryFile(mode='wb', suffix='.mrs', delete=False) as tmp_in:
                    tmp_in.write(response.content)
                    tmp_path = tmp_in.name
                
                try:
                    return self._read_mrs_file(tmp_path, behavior)
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

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
        if not DOMAIN_PATTERN.match(domain):
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
            if not DOMAIN_PATTERN.match(suffix):
                return None
            return f"DOMAIN-SUFFIX,{suffix}"
        
        if not DOMAIN_PATTERN.match(rule):
            return None
        return f"DOMAIN,{rule}"
    
    def _read_local_rules(self, path: str, rule_format: str, behavior: str = 'classical') -> List[str]:
        """读取本地规则"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if rule_format == 'yaml':
                    data = yaml.safe_load(f)
                    # 处理可能的 payload 嵌套
                    if isinstance(data, dict) and 'payload' in data:
                        return data['payload'] or []
                    return data or []
                elif rule_format == 'mrs':
                    return self._read_mrs_file(path, behavior)
                return f.read().splitlines()
        except Exception as e:
            self.logger.error(f"读取本地规则失败 {path}: {str(e)}")
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

        rule_format = source.get('format', 'yaml')
        source_behavior = source.get('behavior', 'classical')
        
        if source['type'] == 'http':
            rules = self._fetch_http_rules(source['url'], rule_format, source_behavior)
        elif source['type'] == 'file':
            rules = self._read_local_rules(source['path'], rule_format, source_behavior)
        
        """mrs规则后续当作txt格式处理"""
        if rule_format == 'mrs':
            rule_format = 'text'

        converted_rules = []
        for rule in rules:
            if rule is None:
                continue
            cleaned_rule = self._clean_rule(rule)
            transformed_rule = self._transform(cleaned_rule, source_behavior, target_behavior)
            self.logger.debug(f"处理规则: {rule} -> {cleaned_rule} -> {transformed_rule}")
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
            target_format = config.get('format', 'yaml')
            merged_rules = []

            if(target_format == 'mrs' and target_behavior == 'classical'):
                self.logger.info(f"{config.get('path')}: mrs格式不支持classical")
                continue
            
            # 处理每个上游源
            for source_name, source_config in config['upstream'].items():
                rules = self._process_source(source_config, target_behavior)
                merged_rules.extend(rules)
            
            # 去重和排序
            merged_rules = sorted(set(merged_rules))
            
            # 获取输出格式
            output_file = config['path']
            self._write_rules(output_file, merged_rules, target_format, target_behavior)
    
    def _write_rules(self, output_path: str, rules: List[str], rule_format: str = 'yaml', behavior: str = 'classical') -> None:
        """写入规则到文件"""
        try:
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            if rule_format == 'mrs':
                with tempfile.NamedTemporaryFile(mode='w', suffix='.tmp', delete=False, encoding='utf-8') as tmp_in:
                    tmp_path = tmp_in.name
                    self._write_rules(tmp_path, rules, 'text', behavior)

                try:
                    if self._convert_to_mrs(tmp_path, output_path, behavior):
                        self.logger.info(f"已生成 mrs 规则文件: {output_path}, 共 {len(rules)} 条规则")
                    else:
                        self.logger.error(f"生成 mrs 规则文件失败: {output_path}")
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                return
            
            with open(output_path, 'w', encoding='utf-8') as f:
                if not output_path.endswith('.tmp'):
                    f.write(f"# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"# 规则数量: {len(rules)}\n")
                if rule_format == 'yaml':
                    yaml_str = yaml.dump(
                        {'payload': rules}, 
                        allow_unicode=True, 
                        indent=2,
                        default_flow_style=False,
                        sort_keys=False
                    )
                    formatted_yaml = yaml_str.replace('\n-', '\n  -')
                    f.write(formatted_yaml)
                else:
                    for rule in rules:
                        f.write(f"{rule}\n")
            if not output_path.endswith('.tmp'):
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
                return rule if DOMAIN_PATTERN.match(value) else None
            elif rule_type == 'IP-CIDR':
                return rule if IPV4_CIDR_PATTERN.match(value) else None
            elif rule_type == 'IP-CIDR6':
                return rule if IPV6_CIDR_PATTERN.match(value) else None
        except Exception as e:
            self.logger.debug(f"规则验证失败: {rule}, 错误: {str(e)}")
            return None
        return rule

    def _validate_ipcidr_rule(self, rule: str) -> Optional[str]:
        """验证 IP-CIDR 规则格式"""
        if IPV4_CIDR_PATTERN.match(rule):
            return rule
        if IPV6_CIDR_PATTERN.match(rule):
            return rule
        self.logger.debug(f"IP-CIDR 规则验证失败: {rule}")
        return None

    def _validate_domain_rule(self, rule: str) -> Optional[str]:
        """验证域名规则格式"""
        # +.example.com 形式的 suffix 规则需要去掉前缀再验证
        domain = rule[2:] if rule.startswith('+.') else rule
        if DOMAIN_PATTERN.match(domain):
            return rule
        self.logger.debug(f"域名规则验证失败: {rule}")
        return None

    def _read_mrs_file(self, input_path: str, behavior: str) -> List[str]:
        """读取mrs文件"""
        if not self.mihomo_path:
            self.logger.warning("未找到 mihomo，无法读取mrs文件")
            return []

        with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tmp_out:
            output_path = tmp_out.name

        try:
            # mihomo convert-ruleset <behavior> mrs <input> <output>
            cmd = [self.mihomo_path, 'convert-ruleset', behavior, 'mrs', input_path, output_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"读取mrs失败: {result.stderr}")
                return []
            
            with open(output_path, 'r', encoding='utf-8') as f:
                return f.read().splitlines()
                
        except Exception as e:
            self.logger.error(f"读取mrs失败: {str(e)}")
            return []
        finally:
            if os.path.exists(output_path):
                try:
                    os.unlink(output_path)
                except OSError as e:
                    self.logger.debug(f"清理临时文件失败 {output_path}: {e}")

    def _convert_to_mrs(self, input_path: str, output_path: str, behavior: str) -> bool:
        """将 text 规则文件转换为 mrs 格式"""
        if not self.mihomo_path:
            self.logger.error("未找到 mihomo，无法生成 mrs 文件")
            return False
            
        try:
            # mihomo convert-ruleset <behavior> yaml <input> <output>
            cmd = [self.mihomo_path, 'convert-ruleset', behavior, 'text', input_path, output_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"生成 mrs 失败: {result.stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"生成 mrs 过程中发生错误: {str(e)}")
            return False

def main():
    merger = RulesMerger('config.yaml')
    merger.merge_rules()

if __name__ == '__main__':
    main()