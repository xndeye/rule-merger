import yaml
import json
import subprocess
import tempfile
import requests
import os
import logging
from typing import List, Dict, Optional, Any
import re
import ipaddress
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

DOMAIN_PATTERN = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*$')
MIHOMO_PATH = 'mihomo'
SING_BOX_PATH = 'sing-box'
SING_BOX_RULESET_VERSION = 4


class RulesMerger:
    def __init__(self, config_path: str):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.mihomo_path = MIHOMO_PATH
        self.sing_box_path = SING_BOX_PATH
        self._transformers = {
            ('classical', 'ipcidr'): self._classical_to_ipcidr,
            ('classical', 'domain'): self._classical_to_domain,
            ('ipcidr', 'classical'): self._ipcidr_to_classical,
            ('domain', 'classical'): self._domain_to_classical,
            ('classical', 'sing-box'): self._classical_to_sing_box,
            ('domain', 'sing-box'): self._domain_to_sing_box,
            ('ipcidr', 'sing-box'): self._ipcidr_to_sing_box,
            ('sing-box', 'classical'): self._sing_box_to_classical,
            ('sing-box', 'domain'): self._sing_box_to_domain,
            ('sing-box', 'ipcidr'): self._sing_box_to_ipcidr
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

    def _make_temp_path(self, suffix: str) -> str:
        """创建临时文件路径并立即关闭句柄，方便外部工具读写。"""
        fd, path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        return path
    
    def _fetch_http_rules(self, url: str, rule_format: str, behavior: str = 'classical') -> List[str]:
        """获取在线规则"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            if rule_format == 'json':
                return self._read_sing_box_source(response.text)

            if rule_format == 'srs':
                tmp_path = self._make_temp_path('.srs')
                with open(tmp_path, 'wb') as tmp_in:
                    tmp_in.write(response.content)

                try:
                    return self._read_srs_file(tmp_path)
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
            
            content_type = response.headers.get('content-type', '')
            # rule_format 优先；仅当格式未明确指定时依赖 Content-Type / URL 后缀推断
            is_yaml = (rule_format == 'yaml') or (
                rule_format not in ('mrs', 'text', 'json', 'srs') and
                ('yaml' in content_type or url.endswith(('.yml', '.yaml')))
            )
            if is_yaml:
                data = yaml.safe_load(response.text)
                return self._extract_yaml_rules(data, url)
            
            if rule_format == 'mrs':
                tmp_path = self._make_temp_path('.mrs')
                with open(tmp_path, 'wb') as tmp_in:
                    tmp_in.write(response.content)
                
                try:
                    return self._read_mrs_file(tmp_path, behavior)
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

            return response.text.splitlines()
        except Exception as e:
            self.logger.error(f"获取规则失败 {url}: {str(e)}", exc_info=True)
            return []
    
    def _transform(self, rule: str, source_behavior: str, target_behavior: str) -> List[str]:
        """转换规则格式"""
        if not rule:
            return []
            
        if source_behavior == target_behavior:
            validators = {
                'classical': self._validate_classical_rule,
                'ipcidr': self._validate_ipcidr_rule,
                'domain': self._validate_domain_rule,
                'sing-box': self._validate_sing_box_rule
            }
            validator = validators.get(source_behavior)
            if validator:
                validated = validator(rule)
                return [validated] if validated else []
            return [rule]
            
        transformer = self._transformers.get((source_behavior, target_behavior))
        if not transformer:
            return []
            
        transformed = transformer(rule)
        if not transformed:
            return []
        if isinstance(transformed, list):
            return transformed
        return [transformed]

    def _classical_to_ipcidr(self, rule: str) -> Optional[str]:
        """将经典规则转换为IP-CIDR规则"""
        parts = rule.split(',')
        if len(parts) < 2:
            return None
        
        suffix = parts[0].strip()
        ipcidr = parts[1].strip()
        if not (suffix == 'IP-CIDR' or suffix == 'IP-CIDR6'):
            return None
        return self._validate_ipcidr_rule(ipcidr)
    
    def _classical_to_domain(self, rule: str) -> Optional[str]:
        """将经典规则转换为DOMAIN规则"""
        parts = rule.split(',')
        if len(parts) < 2:
            return None
        
        suffix = parts[0].strip()
        domain = parts[1].strip()
        # 验证域名格式
        if not DOMAIN_PATTERN.match(domain):
            return None
            
        if suffix == 'DOMAIN':
            return domain
        elif suffix == 'DOMAIN-SUFFIX':
            return '+.' + domain
        return None
    
    def _ipcidr_to_classical(self, rule: str) -> Optional[str]:
        """将IP-CIDR规则转换为经典规则"""
        ip_version = self._get_ipcidr_version(rule)
        if not ip_version:
            return None
        if ip_version == 6:
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
            if rule_format == 'mrs':
                return self._read_mrs_file(path, behavior)
            if rule_format == 'srs':
                return self._read_srs_file(path)

            with open(path, 'r', encoding='utf-8') as f:
                if rule_format == 'json':
                    return self._read_sing_box_source(f.read())
                if rule_format == 'yaml':
                    data = yaml.safe_load(f)
                    return self._extract_yaml_rules(data, path)
                return f.read().splitlines()
        except Exception as e:
            self.logger.error(f"读取本地规则失败 {path}: {str(e)}")
            return []

    def _extract_yaml_rules(self, data: Any, source: str) -> List[str]:
        """从 YAML 内容中提取规则列表。"""
        if data is None:
            return []
        if isinstance(data, dict):
            payload = data.get('payload')
            if isinstance(payload, list):
                return payload
            self.logger.warning(f"YAML规则缺少有效payload列表: {source}")
            return []
        if isinstance(data, list):
            return data
        self.logger.warning(f"YAML规则格式不支持: {source}")
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
        rule_format = source.get('format', 'yaml')
        default_behavior = 'sing-box' if rule_format in ('json', 'srs') else 'classical'
        source_behavior = source.get('behavior', default_behavior)

        source_type = source.get('type')
        if source_type == 'http':
            url = source.get('url')
            if not url:
                self.logger.warning("http规则源缺少url")
                return []
            rules = self._fetch_http_rules(url, rule_format, source_behavior)
        elif source_type == 'file':
            path = source.get('path')
            if not path:
                self.logger.warning("file规则源缺少path")
                return []
            rules = self._read_local_rules(path, rule_format, source_behavior)
        else:
            self.logger.warning(f"不支持的规则源类型: {source_type}")
            return []

        converted_rules = []
        for rule in rules:
            if rule is None:
                continue
            cleaned_rule = rule if source_behavior == 'sing-box' else self._clean_rule(str(rule))
            transformed_rules = self._transform(cleaned_rule, source_behavior, target_behavior)
            self.logger.debug(f"处理规则: {rule} -> {cleaned_rule} -> {transformed_rules}")
            if not transformed_rules:
                continue
            converted_rules.extend(transformed_rules)
        
        return converted_rules
    
    def merge_rules(self) -> None:
        """合并所有规则并生成文件"""
        for config in self.config:
            if 'upstream' not in config or not config.get('path'):
                continue
            
            # 获取目标格式（整个配置文件的输出格式）
            target_format = config.get('format', 'yaml')
            default_behavior = 'sing-box' if target_format in ('json', 'srs') else 'classical'
            target_behavior = config.get('behavior', default_behavior)
            merged_rules = []

            if target_format == 'mrs' and target_behavior not in ('domain', 'ipcidr'):
                self.logger.info(f"{config.get('path')}: mrs格式仅支持domain/ipcidr")
                continue
            
            # 处理每个上游源
            for source_config in config['upstream'].values():
                rules = self._process_source(source_config, target_behavior)
                merged_rules.extend(rules)
            
            # 去重和排序
            merged_rules = sorted(set(merged_rules))
            
            # 获取输出格式
            output_file = config['path']
            self._write_rules(
                output_file,
                merged_rules,
                target_format,
                target_behavior,
                config.get('version', SING_BOX_RULESET_VERSION)
            )


    def _write_rules(
        self,
        output_path: str,
        rules: List[str],
        rule_format: str = 'yaml',
        behavior: str = 'classical',
        version: int = SING_BOX_RULESET_VERSION
    ) -> None:
        """写入规则到文件"""
        try:
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            if rule_format == 'mrs':
                tmp_path = self._make_temp_path('.tmp')
                self._write_rules(tmp_path, rules, 'text', behavior, version)

                try:
                    if self._convert_to_mrs(tmp_path, output_path, behavior):
                        self._log_generated_rule_file('mrs', output_path, len(rules))
                    else:
                        self.logger.error(f"生成 mrs 规则文件失败: {output_path}")
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                return

            if rule_format == 'srs':
                tmp_path = self._make_temp_path('.json')
                self._write_sing_box_source(tmp_path, rules, behavior, version)

                try:
                    if self._convert_to_srs(tmp_path, output_path):
                        self._log_generated_rule_file('srs', output_path, len(rules))
                    else:
                        self.logger.error(f"生成 srs 规则文件失败: {output_path}")
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                return

            if rule_format == 'json':
                self._write_sing_box_source(output_path, rules, behavior, version)
                self._log_generated_rule_file('json', output_path, len(rules))
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
                self._log_generated_rule_file(rule_format, output_path, len(rules))
        except Exception as e:
            self.logger.error(f"写入规则文件失败: {str(e)}", exc_info=True)
            raise

    def _log_generated_rule_file(self, rule_format: str, output_path: str, rule_count: int) -> None:
        self.logger.info(f"已生成 {rule_format} 规则文件: {output_path}, 共 {rule_count} 条规则")

    def _write_sing_box_source(
        self,
        output_path: str,
        rules: List[str],
        behavior: str,
        version: int = SING_BOX_RULESET_VERSION
    ) -> None:
        """写入 sing-box source rule-set JSON。"""
        rule_set = {
            'version': version,
            'rules': self._to_sing_box_rules(rules, behavior)
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(rule_set, f, ensure_ascii=False, indent=2)
            f.write('\n')

    def _to_sing_box_rules(self, rules: List[str], behavior: str) -> List[Dict[str, Any]]:
        """将当前规则转换为 sing-box headless rule。"""
        if behavior == 'sing-box':
            sing_box_rules = []
            for rule in rules:
                parsed_rule = self._parse_sing_box_rule(rule)
                if parsed_rule is None:
                    self.logger.debug(f"跳过无法解析的 sing-box 规则: {rule}")
                    continue
                sing_box_rules.append(parsed_rule)
            return sing_box_rules

        sing_box_rule = {
            'domain': [],
            'domain_suffix': [],
            'domain_keyword': [],
            'domain_regex': [],
            'ip_cidr': []
        }

        for rule in rules:
            converted = self._to_sing_box_item(rule, behavior)
            if not converted:
                self.logger.debug(f"跳过无法转换为 sing-box 的规则: {rule}")
                continue
            key, value = converted
            sing_box_rule[key].append(value)

        compact_rule = {
            key: sorted(set(values))
            for key, values in sing_box_rule.items()
            if values
        }
        return [compact_rule] if compact_rule else []

    def _to_sing_box_item(self, rule: str, behavior: str) -> Optional[tuple[str, str]]:
        if behavior == 'domain':
            if rule.startswith('+.'):
                return 'domain_suffix', rule[2:]
            return 'domain', rule

        if behavior == 'ipcidr':
            return 'ip_cidr', rule

        if behavior != 'classical':
            return None

        parts = [part.strip() for part in rule.split(',')]
        if len(parts) < 2:
            return None

        rule_type = parts[0]
        value = parts[1]
        mapping = {
            'DOMAIN': 'domain',
            'DOMAIN-SUFFIX': 'domain_suffix',
            'DOMAIN-KEYWORD': 'domain_keyword',
            'DOMAIN-REGEX': 'domain_regex',
            'IP-CIDR': 'ip_cidr',
            'IP-CIDR6': 'ip_cidr'
        }
        target_key = mapping.get(rule_type)
        if not target_key:
            return None
        return target_key, value

    def _read_sing_box_source(self, content: str) -> List[str]:
        """读取 sing-box source rule-set JSON，返回规范化 headless rule。"""
        try:
            data = json.loads(content.lstrip('\ufeff'))
        except json.JSONDecodeError as e:
            self.logger.error(f"sing-box json 解析失败: {e}")
            return []

        if not isinstance(data, dict):
            self.logger.error("sing-box json 顶层必须是对象")
            return []

        rules = data.get('rules', [])
        if not isinstance(rules, list):
            self.logger.error("sing-box json rules 必须是列表")
            return []

        normalized_rules = []
        for rule in rules:
            normalized_rule = self._normalize_sing_box_rule(rule)
            if normalized_rule:
                normalized_rules.append(normalized_rule)
        return normalized_rules

    def _normalize_sing_box_rule(self, rule: Any) -> Optional[str]:
        """将 sing-box headless rule 规范化为可去重的 JSON 字符串。"""
        if not isinstance(rule, dict):
            return None
        return json.dumps(rule, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

    def _parse_sing_box_rule(self, rule: str) -> Optional[Dict[str, Any]]:
        try:
            parsed = json.loads(rule)
        except (TypeError, json.JSONDecodeError):
            return None
        return parsed if isinstance(parsed, dict) else None

    def _validate_sing_box_rule(self, rule: str) -> Optional[str]:
        parsed = self._parse_sing_box_rule(rule)
        if parsed is None:
            self.logger.debug(f"sing-box 规则验证失败: {rule}")
            return None
        return self._normalize_sing_box_rule(parsed)

    def _classical_to_sing_box(self, rule: str) -> Optional[str]:
        if not self._validate_classical_rule(rule):
            return None
        item = self._to_sing_box_item(rule, 'classical')
        if not item:
            return None
        key, value = item
        return self._normalize_sing_box_rule({key: [value]})

    def _domain_to_sing_box(self, rule: str) -> Optional[str]:
        if not self._validate_domain_rule(rule):
            return None
        item = self._to_sing_box_item(rule, 'domain')
        if not item:
            return None
        key, value = item
        return self._normalize_sing_box_rule({key: [value]})

    def _ipcidr_to_sing_box(self, rule: str) -> Optional[str]:
        if not self._validate_ipcidr_rule(rule):
            return None
        item = self._to_sing_box_item(rule, 'ipcidr')
        if not item:
            return None
        key, value = item
        return self._normalize_sing_box_rule({key: [value]})

    def _sing_box_to_domain(self, rule: str) -> List[str]:
        parsed = self._parse_sing_box_rule(rule)
        if parsed is None:
            return []

        rules = []
        for item in self._iter_sing_box_rules(parsed):
            for domain in self._as_list(item.get('domain')):
                if isinstance(domain, str) and self._validate_domain_rule(domain):
                    rules.append(domain)
            for suffix in self._as_list(item.get('domain_suffix')):
                if isinstance(suffix, str):
                    suffix = suffix[1:] if suffix.startswith('.') else suffix
                    domain_rule = f"+.{suffix}"
                    if self._validate_domain_rule(domain_rule):
                        rules.append(domain_rule)
        return rules

    def _sing_box_to_ipcidr(self, rule: str) -> List[str]:
        parsed = self._parse_sing_box_rule(rule)
        if parsed is None:
            return []

        rules = []
        for item in self._iter_sing_box_rules(parsed):
            for ipcidr in self._as_list(item.get('ip_cidr')):
                if isinstance(ipcidr, str) and self._validate_ipcidr_rule(ipcidr):
                    rules.append(ipcidr)
        return rules

    def _sing_box_to_classical(self, rule: str) -> List[str]:
        parsed = self._parse_sing_box_rule(rule)
        if parsed is None:
            return []

        rules = []
        for item in self._iter_sing_box_rules(parsed):
            for domain in self._as_list(item.get('domain')):
                if isinstance(domain, str):
                    classical_rule = f"DOMAIN,{domain}"
                    if self._validate_classical_rule(classical_rule):
                        rules.append(classical_rule)
            for suffix in self._as_list(item.get('domain_suffix')):
                if isinstance(suffix, str):
                    suffix = suffix[1:] if suffix.startswith('.') else suffix
                    classical_rule = f"DOMAIN-SUFFIX,{suffix}"
                    if self._validate_classical_rule(classical_rule):
                        rules.append(classical_rule)
            for keyword in self._as_list(item.get('domain_keyword')):
                if isinstance(keyword, str):
                    rules.append(f"DOMAIN-KEYWORD,{keyword}")
            for regex_rule in self._as_list(item.get('domain_regex')):
                if isinstance(regex_rule, str):
                    rules.append(f"DOMAIN-REGEX,{regex_rule}")
            for ipcidr in self._as_list(item.get('ip_cidr')):
                if not isinstance(ipcidr, str):
                    continue
                classical_rule = f"IP-CIDR6,{ipcidr}" if ':' in ipcidr else f"IP-CIDR,{ipcidr}"
                if self._validate_classical_rule(classical_rule):
                    rules.append(classical_rule)
        return rules

    def _iter_sing_box_rules(self, rule: Dict[str, Any]) -> List[Dict[str, Any]]:
        rules = [rule]
        if rule.get('type') == 'logical':
            for nested_rule in self._as_list(rule.get('rules')):
                if isinstance(nested_rule, dict):
                    rules.extend(self._iter_sing_box_rules(nested_rule))
        return rules

    def _as_list(self, value: Any) -> List[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]
    
    def _validate_classical_rule(self, rule: str) -> Optional[str]:
        """验证经典规则格式"""
        try:
            parts = rule.split(',')
            if len(parts) < 2:
                return None
                
            rule_type = parts[0]
            value = parts[1].strip()

            rule = ','.join(part.strip() for part in parts)
                
            if rule_type in {'DOMAIN', 'DOMAIN-SUFFIX'}:
                return rule if DOMAIN_PATTERN.match(value) else None
            elif rule_type == 'IP-CIDR':
                return rule if self._get_ipcidr_version(value) == 4 else None
            elif rule_type == 'IP-CIDR6':
                return rule if self._get_ipcidr_version(value) == 6 else None
            return rule
        except Exception as e:
            self.logger.debug(f"规则验证失败: {rule}, 错误: {str(e)}")
            return None

    def _validate_ipcidr_rule(self, rule: str) -> Optional[str]:
        """验证 IP-CIDR 规则格式"""
        if self._get_ipcidr_version(rule):
            return rule
        self.logger.debug(f"IP-CIDR 规则验证失败: {rule}")
        return None

    def _get_ipcidr_version(self, rule: str) -> Optional[int]:
        try:
            return ipaddress.ip_network(rule, strict=False).version
        except ValueError:
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

        output_path = self._make_temp_path('.txt')

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

    def _read_srs_file(self, input_path: str) -> List[str]:
        """读取 sing-box srs 文件。"""
        if not self.sing_box_path:
            self.logger.warning("未找到 sing-box，无法读取srs文件")
            return []

        output_path = self._make_temp_path('.json')

        try:
            cmd = [self.sing_box_path, 'rule-set', 'decompile', '--output', output_path, input_path]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                self.logger.error(f"读取srs失败: {result.stderr}")
                return []

            with open(output_path, 'r', encoding='utf-8') as f:
                return self._read_sing_box_source(f.read())
        except Exception as e:
            self.logger.error(f"读取srs失败: {str(e)}")
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

    def _convert_to_srs(self, input_path: str, output_path: str) -> bool:
        """将 sing-box source JSON 转换为 srs 格式"""
        if not self.sing_box_path:
            self.logger.error("未找到 sing-box，无法生成 srs 文件")
            return False

        try:
            cmd = [self.sing_box_path, 'rule-set', 'compile', '--output', output_path, input_path]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                self.logger.error(f"生成 srs 失败: {result.stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"生成 srs 过程中发生错误: {str(e)}")
            return False

def main():
    merger = RulesMerger('config.yaml')
    merger.merge_rules()

if __name__ == '__main__':
    main()
