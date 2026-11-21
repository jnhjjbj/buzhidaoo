---
title: 真正关掉 Windows 更新：为什么你改了十遍都没用
date: 2026-11-21 20:00:00
description: Windows 11 家庭版会主动删掉你的更新策略，WaaSMedicSvc 会把你的服务设置还原，hosts 还被 Steam++ 接管了。于是写了个能压住它、又能一键还原的脚本，已开源。
categories:
  - 工具
tags:
  - Windows
  - PowerShell
  - 开源
---

“我把 Windows 更新关了，怎么还在偷偷下载？”

这句话我见过太多次。自己也试过：服务停了、任务禁了、组策略改了、hosts 也加了。
**重启一次，全部还原。**

后来花了一晚上把这件事查到底，终于知道问题在哪了 —— 不是你操作不对，是微软有三道锁。

---

## 第一道锁：服务是「触发器启动」

你以为：

```
wuauserv（Windows Update）→ 设成禁用 → 完事
```

实际上：

```
UsoSvc（更新编排器）自己会起来
    ↓
它发现 wuauserv 没跑
    ↓
把 wuauserv 拉起来
```

`UsoSvc` 不是普通服务，是**触发器启动**（trigger-start）。
你把 `wuauserv` 设成禁用，它照样能被拉起来。
**必须两个一起按死。**

---

## 第二道锁：`WaaSMedicSvc` 专门负责还原

这个服务全名是 Windows Update Medic Service（更新医生）。

它的工作就是：**发现你的更新配置被改了，改回去。**

而且它受 **TrustedInstaller** 保护：

```powershell
PS> Set-Service WaaSMedicSvc -StartupType Disabled
Set-Service : 无法配置服务 "Windows 更新医生服务"，Access is denied
```

管理员也没用。要这样才能动它：

```powershell
takeown /f "HKLM\SYSTEM\CurrentControlSet\Services\WaaSMedicSvc"
# 然后改注册表 ACL，把 Start 设成 4
```

**这才是关键的一步。** 不拿下它，前面做的全是白工。

---

## 第三道锁：家庭版根本不支持「自动更新」策略

网上教程都会让你改这个：

```
HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU
    NoAutoUpdate = 1
```

我本机实测（Windows 11 家庭版 26200）：

```
19:00:00  写入 NoAutoUpdate = 1
19:02:00  键不存在了
```

**家庭版不支持这个策略，系统会主动把它删掉。**

专业版才认。家庭版唯一有效的路，就是**服务层禁用**。

---

## 还有一个坑：你的 hosts 不是你的

想从 DNS 层屏蔽？先看看这个：

```powershell
Get-Content C:\Windows\System32\drivers\etc\hosts -Tail 5
```

如果你装了 **Steam++ / Watt Toolkit**，会看到：

```
# Steam++ Start
...
# Steam++ End
```

**hosts 由它接管。** 你手写进去的阻断条目，刷新一次就被覆盖掉。

这就是为什么很多人「明明加了 hosts 还是没用」。

---

## 所以做了这个工具

既然关起来这么费劲，干脆做成脚本，而且**必须能一键还原**。

仓库：[**jnhjjbj/win11-wu-off**](https://github.com/jnhjjbj/win11-wu-off)

```
wu-off.ps1      关闭 / 查看 / 还原
wu-guard.ps1    守护：把被系统还原的设置压回去
disable.bat     双击关闭（自动提权）
restore.bat     双击还原（自动提权）
```

零依赖，纯 PowerShell，兼容 Windows PowerShell 5.1。

---

## 它到底改了什么

| 层 | 动作 |
|---|---|
| 服务 | `wuauserv` / `UsoSvc` / `WaaSMedicSvc` → **Stopped + Disabled** |
| 策略 | 隐藏更新入口、禁止自动装驱动、关闭 P2P 分发 |
| 计划任务 | 禁用 `UpdateOrchestrator` 下 4 个更新任务 |
| 守护 | 登录时 + 每 30 分钟复查并压回去 |

关键代码就三行：

```powershell
foreach ($n in @('wuauserv','UsoSvc','WaaSMedicSvc')) {
    Stop-Service -Name $n -Force
    Set-Service  -Name $n -StartupType Disabled
}
```

看起来简单，但**少了 `WaaSMedicSvc`，前两行会在几分钟内被还原**。

---

## 还原

任何改动都是可逆的：

```powershell
.\wu-off.ps1 -Restore
```

还原服务启动类型、删掉策略键、重新启用更新任务。建议还原后重启一次。

---

## 说点实话

这个脚本**不建议给所有人用**。

```
✓ 适合：个人机器、流量紧张、不想被强制重启打断工作
✗ 不适合：公司电脑、服务器、你指望它跑安全补丁的机器
```

代价很明确：**不再收到安全补丁**。

我把风险写进 README 了，装之前请看一眼。出问题就 `restore.bat`，别硬撑着。

---

## 最后

Windows 的更新机制设计得挺「固执」的 —— 三道锁，每一道都够你查半天。

如果你也卡在「关了又回来」这一步，希望这个仓库能省你一个晚上。

> 代码：[github.com/jnhjjbj/win11-wu-off](https://github.com/jnhjjbj/win11-wu-off)
> 协议：MIT
