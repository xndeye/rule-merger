# Rule Merger

![Python Version](https://img.shields.io/badge/Python-3%2B-blue?)
![Build Status](https://img.shields.io/github/actions/workflow/status/xndeye/rule-merger/resolve.yml?branch=master)

定时合并 mihomo、sing-box 规则，构建自用规则集

- [x] 支持 `yaml`、`mrs`、`text`、`json`、`srs` 文件格式 [^1]
- [x] 支持 `domain`、`ipcidr`、`classical`、`sing-box` 规则格式
- [x] 支持规则格式互转

## 如何使用

> [!TIP]
> 亦可 Fork 本仓库后使用 Actions 进行自动化构建

1. 安装 `python` 以及必要依赖
   ```shell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. 编辑 `config.yaml` 以列表形式定义需要生成的文件以及其上游规则，基本格式与 Mihomo rule-providers 一致

    ```yaml
    - path: output/reject.yml
      format: yaml         # options: yaml, mrs, text, json, srs
      behavior: classical  # options: domain, ipcidr, classical, sing-box
      upstream:
    
        local_reject:
          type: http
          path: "local/reject.txt"
          format: text
          behavior: classical
    
        xndeye_reject:
          type: http
          url: "https://raw.githubusercontent.com/xndeye/adblock_list/refs/heads/release/clash.yaml"
          format: yaml
          behavior: domain
    ```

3. 配置 Mihomo 路径 (使用 `mrs` 格式必要条件)
   - 修改 `rule_merger.py` 的 `MIHOMO_PATH` 字段  
   - 或将 `mihomo` 可执行文件加入 `/usr/local/bin/` 或 `$PATH` 环境变量中

4. 配置 sing-box 路径 (使用 `srs` 格式必要条件)
   - 修改 `rule_merger.py` 的 `SING_BOX_PATH` 字段
   - 或将 `sing-box` 可执行文件加入 `/usr/local/bin/` 或 `$PATH` 环境变量中
   - GitHub Actions 固定使用 sing-box `v1.13.13`，默认生成 rule-set version `4`

5. 执行脚本

   ```shell
   python rule_merger.py
   ```

## 规则列表

| 文件                   | 介绍         |          github           |            ghproxy            |            jsdelivr            |
|----------------------|:-----------|:-------------------------:|:-----------------------------:|:------------------------------:|
| `reject`        | 广告域名       | [mrs][reject-raw] [yaml][reject-yaml] [json][reject-json] [srs][reject-srs] | [mrs][reject-raw-ghproxy] [yaml][reject-yaml-ghproxy] [json][reject-json-ghproxy] [srs][reject-srs-ghproxy] | [mrs][reject-raw-jsdelivr] [yaml][reject-yaml-jsdelivr] [json][reject-json-jsdelivr] [srs][reject-srs-jsdelivr] |
| `reject@ip`     | 广告IP       | [mrs][reject@ip-raw] [yaml][reject@ip-yaml] [json][reject@ip-json] [srs][reject@ip-srs] | [mrs][reject@ip-raw-ghproxy] [yaml][reject@ip-yaml-ghproxy] [json][reject@ip-json-ghproxy] [srs][reject@ip-srs-ghproxy] | [mrs][reject@ip-raw-jsdelivr] [yaml][reject@ip-yaml-jsdelivr] [json][reject@ip-json-jsdelivr] [srs][reject@ip-srs-jsdelivr] |
| `direct`        | 推荐直连域名     | [mrs][direct-raw] [yaml][direct-yaml] [json][direct-json] [srs][direct-srs] | [mrs][direct-raw-ghproxy] [yaml][direct-yaml-ghproxy] [json][direct-json-ghproxy] [srs][direct-srs-ghproxy] | [mrs][direct-raw-jsdelivr] [yaml][direct-yaml-jsdelivr] [json][direct-json-jsdelivr] [srs][direct-srs-jsdelivr] |
| `direct@ip`     | 推荐直连IP     | [mrs][direct@ip-raw] [yaml][direct@ip-yaml] [json][direct@ip-json] [srs][direct@ip-srs] | [mrs][direct@ip-raw-ghproxy] [yaml][direct@ip-yaml-ghproxy] [json][direct@ip-json-ghproxy] [srs][direct@ip-srs-ghproxy] | [mrs][direct@ip-raw-jsdelivr] [yaml][direct@ip-yaml-jsdelivr] [json][direct@ip-json-jsdelivr] [srs][direct@ip-srs-jsdelivr] |
| `microsoft@cn`  | 微软中国域名     | [mrs][microsoft@cn-raw] [yaml][microsoft@cn-yaml] [json][microsoft@cn-json] [srs][microsoft@cn-srs] | [mrs][microsoft@cn-raw-ghproxy] [yaml][microsoft@cn-yaml-ghproxy] [json][microsoft@cn-json-ghproxy] [srs][microsoft@cn-srs-ghproxy] | [mrs][microsoft@cn-raw-jsdelivr] [yaml][microsoft@cn-yaml-jsdelivr] [json][microsoft@cn-json-jsdelivr] [srs][microsoft@cn-srs-jsdelivr] |
| `apple@cn`      | 苹果中国域名     | [mrs][apple@cn-raw] [yaml][apple@cn-yaml] [json][apple@cn-json] [srs][apple@cn-srs] | [mrs][apple@cn-raw-ghproxy] [yaml][apple@cn-yaml-ghproxy] [json][apple@cn-json-ghproxy] [srs][apple@cn-srs-ghproxy] | [mrs][apple@cn-raw-jsdelivr] [yaml][apple@cn-yaml-jsdelivr] [json][apple@cn-json-jsdelivr] [srs][apple@cn-srs-jsdelivr] |
| `steam@cn`      | Steam 中国域名 | [mrs][steam@cn-raw] [yaml][steam@cn-yaml] [json][steam@cn-json] [srs][steam@cn-srs] | [mrs][steam@cn-raw-ghproxy] [yaml][steam@cn-yaml-ghproxy] [json][steam@cn-json-ghproxy] [srs][steam@cn-srs-ghproxy] | [mrs][steam@cn-raw-jsdelivr] [yaml][steam@cn-yaml-jsdelivr] [json][steam@cn-json-jsdelivr] [srs][steam@cn-srs-jsdelivr] |
| `ai`            | AI相关域名     | [mrs][ai-raw] [yaml][ai-yaml] [json][ai-json] [srs][ai-srs] | [mrs][ai-raw-ghproxy] [yaml][ai-yaml-ghproxy] [json][ai-json-ghproxy] [srs][ai-srs-ghproxy] | [mrs][ai-raw-jsdelivr] [yaml][ai-yaml-jsdelivr] [json][ai-json-jsdelivr] [srs][ai-srs-jsdelivr] |
| `proxy`         | 推荐代理域名     | [mrs][proxy-raw] [yaml][proxy-yaml] [json][proxy-json] [srs][proxy-srs] | [mrs][proxy-raw-ghproxy] [yaml][proxy-yaml-ghproxy] [json][proxy-json-ghproxy] [srs][proxy-srs-ghproxy] | [mrs][proxy-raw-jsdelivr] [yaml][proxy-yaml-jsdelivr] [json][proxy-json-jsdelivr] [srs][proxy-srs-jsdelivr] |
| `proxy@ip`      | 推荐代理IP     | [mrs][proxy@ip-raw] [yaml][proxy@ip-yaml] [json][proxy@ip-json] [srs][proxy@ip-srs] | [mrs][proxy@ip-raw-ghproxy] [yaml][proxy@ip-yaml-ghproxy] [json][proxy@ip-json-ghproxy] [srs][proxy@ip-srs-ghproxy] | [mrs][proxy@ip-raw-jsdelivr] [yaml][proxy@ip-yaml-jsdelivr] [json][proxy@ip-json-jsdelivr] [srs][proxy@ip-srs-jsdelivr] |
| `lan@ip`        | 局域网IP      | [mrs][lan@ip-raw] [yaml][lan@ip-yaml] [json][lan@ip-json] [srs][lan@ip-srs] | [mrs][lan@ip-raw-ghproxy] [yaml][lan@ip-yaml-ghproxy] [json][lan@ip-json-ghproxy] [srs][lan@ip-srs-ghproxy] | [mrs][lan@ip-raw-jsdelivr] [yaml][lan@ip-yaml-jsdelivr] [json][lan@ip-json-jsdelivr] [srs][lan@ip-srs-jsdelivr] |
| `lan`           | 局域网域名     | [mrs][lan-raw] [yaml][lan-yaml] [json][lan-json] [srs][lan-srs] | [mrs][lan-raw-ghproxy] [yaml][lan-yaml-ghproxy] [json][lan-json-ghproxy] [srs][lan-srs-ghproxy] | [mrs][lan-raw-jsdelivr] [yaml][lan-yaml-jsdelivr] [json][lan-json-jsdelivr] [srs][lan-srs-jsdelivr] |
| `fakeip-filter` | fakeIP过滤   | [mrs][fakeip-filter-raw] [yaml][fakeip-filter-yaml] [json][fakeip-filter-json] [srs][fakeip-filter-srs] | [mrs][fakeip-filter-raw-ghproxy] [yaml][fakeip-filter-yaml-ghproxy] [json][fakeip-filter-json-ghproxy] [srs][fakeip-filter-srs-ghproxy] | [mrs][fakeip-filter-raw-jsdelivr] [yaml][fakeip-filter-yaml-jsdelivr] [json][fakeip-filter-json-jsdelivr] [srs][fakeip-filter-srs-jsdelivr] |

## 引用来源

- [Sukka Ruleset](https://ruleset.skk.moe)
- [Loyalsoldier/clash-rules](https://github.com/Loyalsoldier/clash-rules)
- [DustinWin/domain-list-custom](https://github.com/DustinWin/domain-list-custom)
- [xndeye/adblock_list](https://github.com/xndeye/adblock_list)
- [ACL4SSR/ACL4SSR](https://github.com/ACL4SSR/ACL4SSR)
- [Accademia/Additional_Rule_For_Clash](https://github.com/Accademia/Additional_Rule_For_Clash)

---

[^1]: **mihomo** 可用格式：`yaml`、`mrs`、`text`，**sing-box** 可用格式：`json`、`srs`


[reject-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/reject.mrs
[reject-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/reject.yaml
[reject-json]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/reject.json
[reject-srs]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/reject.srs

[reject-raw-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/reject.mrs
[reject-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/reject.yaml
[reject-json-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/reject.json
[reject-srs-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/reject.srs

[reject-raw-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/reject.mrs
[reject-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/reject.yaml
[reject-json-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/reject.json
[reject-srs-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/reject.srs

[reject@ip-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/reject@ip.mrs
[reject@ip-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/reject@ip.yaml
[reject@ip-json]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/reject@ip.json
[reject@ip-srs]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/reject@ip.srs

[reject@ip-raw-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/reject@ip.mrs
[reject@ip-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/reject@ip.yaml
[reject@ip-json-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/reject@ip.json
[reject@ip-srs-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/reject@ip.srs

[reject@ip-raw-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/reject@ip.mrs
[reject@ip-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/reject@ip.yaml
[reject@ip-json-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/reject@ip.json
[reject@ip-srs-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/reject@ip.srs

[direct-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/direct.mrs
[direct-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/direct.yaml
[direct-json]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/direct.json
[direct-srs]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/direct.srs

[direct-raw-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/direct.mrs
[direct-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/direct.yaml
[direct-json-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/direct.json
[direct-srs-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/direct.srs

[direct-raw-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/direct.mrs
[direct-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/direct.yaml
[direct-json-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/direct.json
[direct-srs-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/direct.srs

[direct@ip-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/direct@ip.mrs
[direct@ip-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/direct@ip.yaml
[direct@ip-json]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/direct@ip.json
[direct@ip-srs]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/direct@ip.srs

[direct@ip-raw-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/direct@ip.mrs
[direct@ip-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/direct@ip.yaml
[direct@ip-json-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/direct@ip.json
[direct@ip-srs-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/direct@ip.srs

[direct@ip-raw-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/direct@ip.mrs
[direct@ip-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/direct@ip.yaml
[direct@ip-json-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/direct@ip.json
[direct@ip-srs-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/direct@ip.srs

[microsoft@cn-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/microsoft@cn.mrs
[microsoft@cn-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/microsoft@cn.yaml
[microsoft@cn-json]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/microsoft@cn.json
[microsoft@cn-srs]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/microsoft@cn.srs

[microsoft@cn-raw-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/microsoft@cn.mrs
[microsoft@cn-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/microsoft@cn.yaml
[microsoft@cn-json-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/microsoft@cn.json
[microsoft@cn-srs-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/microsoft@cn.srs

[microsoft@cn-raw-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/microsoft@cn.mrs
[microsoft@cn-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/microsoft@cn.yaml
[microsoft@cn-json-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/microsoft@cn.json
[microsoft@cn-srs-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/microsoft@cn.srs

[apple@cn-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/apple@cn.mrs
[apple@cn-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/apple@cn.yaml
[apple@cn-json]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/apple@cn.json
[apple@cn-srs]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/apple@cn.srs

[apple@cn-raw-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/apple@cn.mrs
[apple@cn-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/apple@cn.yaml
[apple@cn-json-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/apple@cn.json
[apple@cn-srs-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/apple@cn.srs

[apple@cn-raw-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/apple@cn.mrs
[apple@cn-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/apple@cn.yaml
[apple@cn-json-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/apple@cn.json
[apple@cn-srs-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/apple@cn.srs

[steam@cn-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/steam@cn.mrs
[steam@cn-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/steam@cn.yaml
[steam@cn-json]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/steam@cn.json
[steam@cn-srs]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/steam@cn.srs

[steam@cn-raw-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/steam@cn.mrs
[steam@cn-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/steam@cn.yaml
[steam@cn-json-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/steam@cn.json
[steam@cn-srs-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/steam@cn.srs

[steam@cn-raw-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/steam@cn.mrs
[steam@cn-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/steam@cn.yaml
[steam@cn-json-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/steam@cn.json
[steam@cn-srs-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/steam@cn.srs

[ai-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/ai.mrs
[ai-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/ai.yaml
[ai-json]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/ai.json
[ai-srs]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/ai.srs

[ai-raw-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/ai.mrs
[ai-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/ai.yaml
[ai-json-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/ai.json
[ai-srs-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/ai.srs

[ai-raw-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/ai.mrs
[ai-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/ai.yaml
[ai-json-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/ai.json
[ai-srs-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/ai.srs

[proxy-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/proxy.mrs
[proxy-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/proxy.yaml
[proxy-json]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/proxy.json
[proxy-srs]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/proxy.srs

[proxy-raw-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/proxy.mrs
[proxy-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/proxy.yaml
[proxy-json-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/proxy.json
[proxy-srs-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/proxy.srs

[proxy-raw-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/proxy.mrs
[proxy-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/proxy.yaml
[proxy-json-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/proxy.json
[proxy-srs-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/proxy.srs

[proxy@ip-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/proxy@ip.mrs
[proxy@ip-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/proxy@ip.yaml
[proxy@ip-json]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/proxy@ip.json
[proxy@ip-srs]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/proxy@ip.srs

[proxy@ip-raw-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/proxy@ip.mrs
[proxy@ip-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/proxy@ip.yaml
[proxy@ip-json-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/proxy@ip.json
[proxy@ip-srs-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/proxy@ip.srs

[proxy@ip-raw-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/proxy@ip.mrs
[proxy@ip-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/proxy@ip.yaml
[proxy@ip-json-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/proxy@ip.json
[proxy@ip-srs-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/proxy@ip.srs

[lan@ip-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/lan@ip.mrs
[lan@ip-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/lan@ip.yaml
[lan@ip-json]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/lan@ip.json
[lan@ip-srs]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/lan@ip.srs

[lan@ip-raw-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/lan@ip.mrs
[lan@ip-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/lan@ip.yaml
[lan@ip-json-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/lan@ip.json
[lan@ip-srs-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/lan@ip.srs

[lan@ip-raw-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/lan@ip.mrs
[lan@ip-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/lan@ip.yaml
[lan@ip-json-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/lan@ip.json
[lan@ip-srs-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/lan@ip.srs

[lan-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/lan.mrs
[lan-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/lan.yaml
[lan-json]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/lan.json
[lan-srs]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/lan.srs

[lan-raw-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/lan.mrs
[lan-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/lan.yaml
[lan-json-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/lan.json
[lan-srs-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/lan.srs

[lan-raw-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/lan.mrs
[lan-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/lan.yaml
[lan-json-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/lan.json
[lan-srs-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/lan.srs

[fakeip-filter-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/fakeip-filter.mrs
[fakeip-filter-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/fakeip-filter.yaml
[fakeip-filter-json]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/fakeip-filter.json
[fakeip-filter-srs]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/fakeip-filter.srs

[fakeip-filter-raw-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/fakeip-filter.mrs
[fakeip-filter-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/fakeip-filter.yaml
[fakeip-filter-json-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/fakeip-filter.json
[fakeip-filter-srs-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/fakeip-filter.srs

[fakeip-filter-raw-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/fakeip-filter.mrs
[fakeip-filter-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/fakeip-filter.yaml
[fakeip-filter-json-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/fakeip-filter.json
[fakeip-filter-srs-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/fakeip-filter.srs
