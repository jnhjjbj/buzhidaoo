---
title: Hello World · 这个站点终于开张了
date: 2026-11-18 21:30:00
cover: /img/cover-3.jpg
description: 折腾了两个晚上，Hexo + Butterfly 的框架总算跑起来了。这篇先记录一下站点结构和踩过的坑。
categories:
  - 随笔
tags:
  - Hexo
  - Butterfly
  - 建站
---

## 为什么又要建一个博客

笔记散在本地 Markdown、备忘录、聊天记录里，找起来全靠运气。扔到线上至少有个能搜的地方，顺带逼自己把东西写完整。

选 Hexo 是因为快：纯静态、生成一秒、扔哪个 CDN 都能跑。主题选了 Butterfly，卡片式的版式对文章多的站比较友好。

## 目录结构

```
blog/
├── _config.yml            # 站点配置（标题、作者、部署）
├── _config.butterfly.yml  # 主题配置（菜单、侧边栏、配色）
├── scaffolds/             # 新建文章的模板
├── source/
│   ├── _posts/            # 文章都在这
│   ├── about/             # 独立页面
│   └── img/               # 图片
└── themes/                # 主题（npm 安装时在 node_modules）
```

两个配置文件容易搞混，记一句就行：**站点的归 `_config.yml`，长相的归 `_config.butterfly.yml`**。

## 常用命令

```bash
hexo new "文章标题"      # 新建文章
hexo generate            # 生成静态文件到 public/
hexo server              # 本地预览 localhost:4000
hexo clean               # 清掉缓存，改配置后先跑这个
hexo deploy              # 按 _config.yml 的 deploy 发布
```

改完配置页面没变化，八成是缓存，`hexo clean && hexo server` 走一遍就好。

## 踩到的坑

1. **`hexo server` 起来是空白页** — 主题目录没装依赖，Butterfly 需要 `hexo-renderer-pug` 和 `hexo-renderer-stylus`，缺一个就渲染不出来。
2. **中文菜单变乱码** — `_config.butterfly.yml` 必须存成 UTF-8 无 BOM，记事本默认会加 BOM。
3. **首页摘要突然变全文** — front-matter 里加 `description`，或者正文里手动插 `<!-- more -->`。
4. **图片 404** — `source/img/` 下的文件对应 `/img/xxx.jpg`，注意开头的斜杠别丢。

## 接下来想做的

- [x] 站点骨架、导航、侧边栏
- [x] 本地搜索、字数统计
- [ ] 评论系统（等有稳定域名再挂 Waline）
- [ ] 把旧的实训笔记迁过来

先这样，能跑就行。
