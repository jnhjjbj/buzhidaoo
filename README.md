# CyberNotes · Hexo + Butterfly 博客

同款环境：**Hexo 8.1 + Butterfly 5.7**，纯静态，可部署到 Netlify / Vercel / GitHub Pages / 任意静态空间。

## 一、跑起来

```bash
cd blog
npm install          # 首次或换了机器才需要
hexo server          # 打开 http://localhost:4000
```

改完配置页面没反应，先 `hexo clean` 再启动。

## 二、改成你自己的

站点信息全在 **`_config.yml`** 开头这几行：

```yaml
title: CyberNotes          # 站点标题（左上角 + 浏览器标签）
subtitle: '记录安全、代码与折腾'
author: CyberNotes         # 博主昵称（侧边栏 + 页脚版权）
url: https://blog.example.com   # 部署后的真实域名
```

> 头像、横幅、封面在 `source/img/`：`avatar.png`、`banner.jpg`、`cover-1~3.jpg`，直接替换同名文件即可。
> 想找回默认蓝，把 `_config.butterfly.yml` 里 `theme_color.enable` 改成 `false`。

## 三、写文章

```bash
hexo new "文章标题"        # 生成 source/_posts/文章标题.md
```

front-matter 模板（照抄改内容）：

```yaml
---
title: 文章标题
date: 2026-11-20 20:00:00
cover: /img/cover-1.jpg      # 不写就用默认封面
description: 一句话摘要，会显示在首页卡片上
categories:
  - 安全实训
tags:
  - Wireshark
---
```

正文里插 `<!-- more -->` 可以手动控制首页截断位置。

## 四、已经配好的东西

| 功能 | 在哪配 | 状态 |
| --- | --- | --- |
| 导航菜单 | `_config.butterfly.yml` → `menu` | 首页/文章/标签/分类/友链/关于/GitHub |
| 本地搜索 | `search.use: local_search` | 已开启，导航栏放大镜可用 |
| 字数与阅读时长 | `wordcount.enable` | 已开启 |
| 目录 TOC | `toc.post` | 已开启，右侧悬浮 |
| 推荐阅读 | `related_post` | 已开启 |
| 访问统计 | `busuanzi` | 已开启（PV/UV） |
| 深浅色切换 | `darkmode` | 已开启 |
| 评论 | `comments.use` | **空着**，见下 |

### 评论系统（暂未接）

Butterfly 支持 Waline / Twikoo / Giscus 等。推荐 Giscus（基于 GitHub Discussions，零成本）：

1. 仓库 Settings → General → Features 勾选 **Discussions**
2. 安装 [giscus app](https://github.com/apps/giscus)
3. 打开 https://giscus.app 填仓库名，拿到 `repo` / `repo_id` / `category_id`
4. 填进 `_config.butterfly.yml` 的 `giscus:` 段，再把 `comments.use` 改成 `Giscus`

## 五、部署

### Netlify（推荐，仓库里已带 `netlify.toml`）

1. 代码推到 GitHub
2. Netlify → New site from Git → 选仓库
3. 构建命令 `hexo generate`，发布目录 `public`（`netlify.toml` 里已写好，通常自动识别）

### GitHub Pages

```bash
npm install hexo-deployer-git --save
```

`_config.yml` 里改：

```yaml
url: https://<用户名>.github.io/<仓库名>
deploy:
  type: git
  repo: https://github.com/<用户名>/<仓库名>.git
  branch: gh-pages
```

然后 `hexo clean && hexo generate && hexo deploy`。仓库名不是 `<用户名>.github.io` 时，还要把 `root` 设成 `/<仓库名>/`。

## 六、目录速查

```
blog/
├── _config.yml            站点配置（标题、作者、URL、部署）
├── _config.butterfly.yml  主题配置（菜单、侧边栏、颜色、评论）
├── netlify.toml           Netlify 构建配置
├── scaffolds/             新建文章的模板
├── source/
│   ├── _posts/            文章
│   ├── img/               图片素材
│   ├── about/             关于页
│   ├── link/              友链页
│   ├── tags/              标签页（type: tags）
│   └── categories/        分类页（type: categories）
└── public/                生成结果（不用手改）
```

## 七、常见问题

**首页空白 / 样式全丢**
主题依赖缺了：`npm i hexo-renderer-pug hexo-renderer-stylus`。

**中文乱码**
配置文件必须 UTF-8 无 BOM，VSCode 右下角确认编码。

**改了配置没生效**
`hexo clean` 后重启。

**搜索没结果**
`_config.yml` 里 `search.path: search.xml`，且 `hexo-generator-searchdb` 已安装；生成后 `public/search.xml` 应该存在。
