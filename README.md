# Rule Merger

![Python Version](https://img.shields.io/badge/Python-3%2B-blue?)
![Build Status](https://img.shields.io/github/actions/workflow/status/xndeye/rule-merger/resolve.yml?branch=master)

定时合并 Mihomo 规则，构建自用规则集

## 如何使用

1. 安装 `python` 以及必要依赖

   ```shell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
2. 编辑 `config.yaml` 以列表形式定义需要生成的文件以及其上游规则，基本格式与 Mihomo rule-providers 一致

    ```
    - path: output/reject.yaml
      format: yaml
      behavior: classical
      upstream:
    
        local_reject:
          type: http
          path: "local/reject.txt"
          format: txt
          behavior: classical
    
        xndeye_reject:
          type: http
          url: "https://raw.githubusercontent.com/xndeye/adblock_list/beta/rule/clash.yaml"
          format: yaml
          behavior: domain
    ```
3. 执行脚本

   ```shell
   python rule_merger.py
   ```

## 规则列表

| 文件                   | 介绍         |          github           |            ghproxy            |            jsdelivr            |
|----------------------|:-----------|:-------------------------:|:-----------------------------:|:------------------------------:|
| `reject.yaml`        | 广告域名       |    [link][reject-raw]     |    [link][reject-ghproxy]     |    [link][reject-jsdelivr]     |
| `reject@ip.yaml`     | 广告IP       |   [link][reject@ip-raw]   |   [link][reject@ip-ghproxy]   |   [link][reject@ip-jsdelivr]   |
| `direct.yaml`        | 推荐直连域名     |    [link][direct-raw]     |    [link][direct-ghproxy]     |    [link][direct-jsdelivr]     |
| `direct@ip.yaml`     | 推荐直连IP     |   [link][direct@ip-raw]   |   [link][direct@ip-ghproxy]   |   [link][direct@ip-jsdelivr]   |
| `microsoft@cn.yaml`  | 微软中国域名     | [link][microsoft@cn-raw]  | [link][microsoft@cn-ghproxy]  | [link][microsoft@cn-jsdelivr]  |
| `apple@cn.yaml`      | 苹果中国域名     |   [link][apple@cn-raw]    |   [link][apple@cn-ghproxy]    |   [link][apple@cn-jsdelivr]    |
| `steam@cn.yaml`      | Steam 中国域名 |   [link][steam@cn-raw]    |   [link][steam@cn-ghproxy]    |   [link][steam@cn-jsdelivr]    |
| `ai.yaml`            | AI相关域名     |      [link][ai-raw]       |      [link][ai-ghproxy]       |      [link][ai-jsdelivr]       |
| `proxy.yaml`         | 推荐代理域名     |     [link][proxy-raw]     |     [link][proxy-ghproxy]     |     [link][proxy-jsdelivr]     |
| `proxy@ip.yaml`      | 推荐代理IP     |   [link][proxy@ip-raw]    |   [link][proxy@ip-ghproxy]    |   [link][proxy@ip-jsdelivr]    |
| `lan@ip.yaml`        | 局域网IP      |    [link][lan@ip-raw]     |    [link][lan@ip-ghproxy]     |    [link][lan@ip-jsdelivr]     |
| `fakeip-filter.yaml` | fakeIP过滤   | [link][fakeip-filter-raw] | [link][fakeip-filter-ghproxy] | [link][fakeip-filter-jsdelivr] |

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
- [DustinWin/ruleset_geodata](https://github.com/DustinWin/ruleset_geodata)
- [xndeye/adblock_list](https://github.com/xndeye/adblock_list)

[reject-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/reject.yaml

[reject-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/reject.yaml

[reject-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/reject.yaml

[reject@ip-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/reject@ip.yaml

[reject@ip-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/reject@ip.yaml

[reject@ip-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/reject@ip.yaml

[direct-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/direct.yaml

[direct-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/direct.yaml

[direct-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/direct.yaml

[direct@ip-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/direct@ip.yaml

[direct@ip-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/direct@ip.yaml

[direct@ip-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/direct@ip.yaml

[microsoft@cn-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/microsoft@cn.yaml

[microsoft@cn-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/microsoft@cn.yaml

[microsoft@cn-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/microsoft@cn.yaml

[apple@cn-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/apple@cn.yaml

[apple@cn-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/apple@cn.yaml

[apple@cn-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/apple@cn.yaml

[steam@cn-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/steam@cn.yaml

[steam@cn-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/steam@cn.yaml

[steam@cn-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/steam@cn.yaml

[ai-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/ai.yaml

[ai-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/ai.yaml

[ai-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/ai.yaml

[proxy-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/proxy.yaml

[proxy-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/proxy.yaml

[proxy-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/proxy.yaml

[proxy@ip-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/proxy@ip.yaml

[proxy@ip-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/proxy@ip.yaml

[proxy@ip-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/proxy@ip.yaml

[lan@ip-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/lan@ip.yaml

[lan@ip-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/lan@ip.yaml

[lan@ip-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/lan@ip.yaml

[fakeip-filter-raw]: https://raw.githubusercontent.com/xndeye/rule-merger/refs/heads/release/fakeip-filter.yaml

[fakeip-filter-ghproxy]: https://ghproxy.net/https://raw.githubusercontent.com/xndeye/rule-merger/release/fakeip-filter.yaml

[fakeip-filter-jsdelivr]: https://fastly.jsdelivr.net/gh/xndeye/rule-merger@release/fakeip-filter.yaml
