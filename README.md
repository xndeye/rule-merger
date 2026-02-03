# Rule Merger

![Python Version](https://img.shields.io/badge/Python-3%2B-blue?)
![Build Status](https://img.shields.io/github/actions/workflow/status/xndeye/rule-merger/resolve.yml?branch=master)

定时合并 Mihomo 规则，构建自用规则集

- [x] 支持 `yaml`、`mrs`、`text` 文件格式
- [x] 支持 `domain`、`ipcidr`、`classical` 规则格式
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
      behavior: classical
      upstream:
    
        local_reject:
          type: http
          path: "local/reject.txt"
          format: txt
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

4. 执行脚本

   ```shell
   python rule_merger.py
   ```

## 规则列表

| 文件                   | 介绍         |          github           |            ghproxy            |            jsdelivr            |
|----------------------|:-----------|:-------------------------:|:-----------------------------:|:------------------------------:|
| `reject`        | 广告域名       | [mrs][reject-raw] [yaml][reject-yaml] | [mrs][reject-ghproxy] [yaml][reject-yaml-ghproxy] | [mrs][reject-jsdelivr] [yaml][reject-yaml-jsdelivr] |
| `reject@ip`     | 广告IP       | [mrs][reject@ip-raw] [yaml][reject@ip-yaml] | [mrs][reject@ip-ghproxy] [yaml][reject@ip-yaml-ghproxy] | [mrs][reject@ip-jsdelivr] [yaml][reject@ip-yaml-jsdelivr] |
| `direct`        | 推荐直连域名     | [mrs][direct-raw] [yaml][direct-yaml] | [mrs][direct-ghproxy] [yaml][direct-yaml-ghproxy] | [mrs][direct-jsdelivr] [yaml][direct-yaml-jsdelivr] |
| `direct@ip`     | 推荐直连IP     | [mrs][direct@ip-raw] [yaml][direct@ip-yaml] | [mrs][direct@ip-ghproxy] [yaml][direct@ip-yaml-ghproxy] | [mrs][direct@ip-jsdelivr] [yaml][direct@ip-yaml-jsdelivr] |
| `microsoft@cn`  | 微软中国域名     | [mrs][microsoft@cn-raw] [yaml][microsoft@cn-yaml] | [mrs][microsoft@cn-ghproxy] [yaml][microsoft@cn-yaml-ghproxy] | [mrs][microsoft@cn-jsdelivr] [yaml][microsoft@cn-yaml-jsdelivr] |
| `apple@cn`      | 苹果中国域名     | [mrs][apple@cn-raw] [yaml][apple@cn-yaml] | [mrs][apple@cn-ghproxy] [yaml][apple@cn-yaml-ghproxy] | [mrs][apple@cn-jsdelivr] [yaml][apple@cn-yaml-jsdelivr] |
| `steam@cn`      | Steam 中国域名 | [mrs][steam@cn-raw] [yaml][steam@cn-yaml] | [mrs][steam@cn-ghproxy] [yaml][steam@cn-yaml-ghproxy] | [mrs][steam@cn-jsdelivr] [yaml][steam@cn-yaml-jsdelivr] |
| `ai`            | AI相关域名     | [mrs][ai-raw] [yaml][ai-yaml] | [mrs][ai-ghproxy] [yaml][ai-yaml-ghproxy] | [mrs][ai-jsdelivr] [yaml][ai-yaml-jsdelivr] |
| `proxy`         | 推荐代理域名     | [mrs][proxy-raw] [yaml][proxy-yaml] | [mrs][proxy-ghproxy] [yaml][proxy-yaml-ghproxy] | [mrs][proxy-jsdelivr] [yaml][proxy-yaml-jsdelivr] |
| `proxy@ip`      | 推荐代理IP     | [mrs][proxy@ip-raw] [yaml][proxy@ip-yaml] | [mrs][proxy@ip-ghproxy] [yaml][proxy@ip-yaml-ghproxy] | [mrs][proxy@ip-jsdelivr] [yaml][proxy@ip-yaml-jsdelivr] |
| `lan@ip`        | 局域网IP      | [mrs][lan@ip-raw] [yaml][lan@ip-yaml] | [mrs][lan@ip-ghproxy] [yaml][lan@ip-yaml-ghproxy] | [mrs][lan@ip-jsdelivr] [yaml][lan@ip-yaml-jsdelivr] |
| `fakeip-filter` | fakeIP过滤   | [mrs][fakeip-filter-raw] [yaml][fakeip-filter-yaml] | [mrs][fakeip-filter-ghproxy] [yaml][fakeip-filter-yaml-ghproxy] | [mrs][fakeip-filter-jsdelivr] [yaml][fakeip-filter-yaml-jsdelivr] |

## 完整规则

自用轻量级 Mihomo 配置 [mihomo.yaml](https://github.com/xndeye/rule-merger/blob/master/mihomo.yaml)  

> [!TIP]
> 1. 基于本仓库规则集编写，包含了分流和去广告，简单易用
> 2. `Fallback` 表示规则集未命中，通常保持 Direct，遇到特定网站无法打开或流量宽裕则可选择跟随 `Select Proxy`
> 3. 非直连域不在本地进行 DNS 解析，故不存在所谓 DNS 泄露
> 4. 请用现有（机场）订阅链接 替换配置中 `此处填写你的订阅地址`，而后将配置导入客户端即可使用
> 5. 如客户端存在配置覆写、功能覆盖等，请自行调整或关闭相应功能

## 引用来源

- [Sukka Ruleset](https://ruleset.skk.moe)
- [Loyalsoldier/clash-rules](https://github.com/Loyalsoldier/clash-rules)
- [DustinWin/domain-list-custom](https://github.com/DustinWin/domain-list-custom)
- [xndeye/adblock_list](https://github.com/xndeye/adblock_list)
- [ACL4SSR/ACL4SSR](https://github.com/ACL4SSR/ACL4SSR)

[reject-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/reject.mrs
[reject-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/reject.yaml

[reject-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/reject.mrs
[reject-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/reject.yaml

[reject-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/reject.mrs
[reject-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/reject.yaml

[reject@ip-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/reject@ip.mrs
[reject@ip-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/reject@ip.yaml

[reject@ip-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/reject@ip.mrs
[reject@ip-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/reject@ip.yaml

[reject@ip-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/reject@ip.mrs
[reject@ip-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/reject@ip.yaml

[direct-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/direct.mrs
[direct-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/direct.yaml

[direct-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/direct.mrs
[direct-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/direct.yaml

[direct-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/direct.mrs
[direct-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/direct.yaml

[direct@ip-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/direct@ip.mrs
[direct@ip-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/direct@ip.yaml

[direct@ip-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/direct@ip.mrs
[direct@ip-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/direct@ip.yaml

[direct@ip-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/direct@ip.mrs
[direct@ip-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/direct@ip.yaml

[microsoft@cn-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/microsoft@cn.mrs
[microsoft@cn-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/microsoft@cn.yaml

[microsoft@cn-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/microsoft@cn.mrs
[microsoft@cn-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/microsoft@cn.yaml

[microsoft@cn-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/microsoft@cn.mrs
[microsoft@cn-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/microsoft@cn.yaml

[apple@cn-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/apple@cn.mrs
[apple@cn-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/apple@cn.yaml

[apple@cn-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/apple@cn.mrs
[apple@cn-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/apple@cn.yaml

[apple@cn-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/apple@cn.mrs
[apple@cn-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/apple@cn.yaml

[steam@cn-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/steam@cn.mrs
[steam@cn-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/steam@cn.yaml

[steam@cn-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/steam@cn.mrs
[steam@cn-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/steam@cn.yaml

[steam@cn-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/steam@cn.mrs
[steam@cn-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/steam@cn.yaml

[ai-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/ai.mrs
[ai-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/ai.yaml

[ai-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/ai.mrs
[ai-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/ai.yaml

[ai-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/ai.mrs
[ai-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/ai.yaml

[proxy-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/proxy.mrs
[proxy-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/proxy.yaml

[proxy-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/proxy.mrs
[proxy-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/proxy.yaml

[proxy-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/proxy.mrs
[proxy-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/proxy.yaml

[proxy@ip-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/proxy@ip.mrs
[proxy@ip-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/proxy@ip.yaml

[proxy@ip-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/proxy@ip.mrs
[proxy@ip-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/proxy@ip.yaml

[proxy@ip-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/proxy@ip.mrs
[proxy@ip-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/proxy@ip.yaml

[lan@ip-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/lan@ip.mrs
[lan@ip-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/lan@ip.yaml

[lan@ip-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/lan@ip.mrs
[lan@ip-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/lan@ip.yaml

[lan@ip-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/lan@ip.mrs
[lan@ip-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/lan@ip.yaml

[fakeip-filter-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/fakeip-filter.mrs
[fakeip-filter-yaml]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/fakeip-filter.yaml

[fakeip-filter-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/fakeip-filter.mrs
[fakeip-filter-yaml-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/fakeip-filter.yaml

[fakeip-filter-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/fakeip-filter.mrs
[fakeip-filter-yaml-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/fakeip-filter.yaml
