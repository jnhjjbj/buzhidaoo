---
title: Wireshark 实践：QQ 登录流量分析
date: 2026-10-26 20:30:00
cover: /img/cover-3.jpg
description: 抓一次 QQ 登录全过程，看看加密应用在网络层到底暴露了什么：域名、协议、包长分布，以及为什么抓不到明文密码。
categories:
  - 安全实训
tags:
  - Wireshark
  - 流量分析
  - 网络抓包
  - 加密
---

抓包是安全里最直观的一课：你以为「加密了就安全」，看到报文才知道暴露了多少元信息。

## 一、抓包准备

- 网卡选实际出口那块（虚拟机桥接时容易选错，抓到全是 0 字节）
- 过滤器先留空，先抓后过滤，避免漏掉握手过程
- 关闭不必要的后台程序，减少噪声

抓完后看 `Statistics → Protocol Hierarchy`，一眼就能看到协议分布。

## 二、登录过程的流量特征

一次 QQ 登录大致能看到这几段：

| 阶段 | 协议 | 特征 |
| --- | --- | --- |
| 域名解析 | DNS | 查询 `*.qq.com` 系列子域 |
| 建连 | TCP | 443 端口，TLS 1.3 握手 |
| 认证 | TLS 应用数据 | 长度固定，内容不可读 |
| 长连接维持 | TCP Keep-Alive | 周期性小包，心跳特征明显 |
| 图片/文件 | HTTP/2 | 复用同一连接 |

DNS 阶段能直接读出来：

```
Standard query 0x1a2b A login.qq.com
Standard query response 0x1a2b A login.qq.com A 203.205.x.x
```

这一步就足以暴露「这个人在用 QQ」以及访问了哪个服务。

## 三、为什么看不到明文密码

因为认证走的是 TLS。握手之后应用数据全部加密，Wireshark 只能告诉你：

- 谁和谁通信（IP / 端口）
- 用了什么协议和版本（TLS 1.3）
- 报文大小和时间间隔
- SNI 里的目标域名（TLS 1.3 默认也加密了，除非用 ESNI/ECH 之前的老实现）

要看内容只有两条路：**拿到会话密钥**（配置 SSLKEYLOGFILE 解 TLS），或者**中间人替换证书**（客户端不校验才行）。公网环境两条都做不到。

## 四、加密之外还暴露了什么

这部分才是重点：

1. **通信对象** — DNS + SNI 直接暴露应用与服务器
2. **行为节奏** — 包长和间隔能推断操作类型（发消息 vs 收图片）
3. **流量指纹** — 不同应用、不同版本的 TLS 指纹（JA3）可被识别
4. **明文残留** — HTTP 站点、未加密的图片 CDN、内嵌的第三方请求

实验里就抓到一个明文 HTTP 请求，把页面里嵌的图片地址全暴露了。

## 五、Wireshark 常用过滤

```text
ip.addr == 203.205.1.1          # 按 IP
tcp.port == 443                 # 按端口
dns.qry.name contains "qq.com"  # 按查询域名
tls.handshake.type == 1         # Client Hello
http.request                    # 所有 HTTP 请求
tcp.analysis.retransmission     # 重传，判断网络质量
tls.alert_message               # 握手失败
```

技巧：右键任意字段 → `Apply as Filter → Selected`，比自己手写快得多。

## 六、小结

加密解决的是**内容保密**，不解决**元数据泄露**。对防御方来说，出向流量的域名和指纹控制，比内容审计更现实；对攻击方（红队）来说，流量层面的异常往往比内容更容易被抓。
