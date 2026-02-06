# 小说章节在线阅读

基于GitHub Pages的在线阅读网站，包含100个章节的完整内容。

## 访问地址

🌐 **GitHub Pages**: https://lolgigeo.github.io/hly/

> 注意：如果CSS/JS资源未正确加载，请确认GitHub Pages设置中的baseurl为`/hly`

## 功能特性

- 📚 100个章节完整内容
- 🔍 章节搜索功能
- 📱 响应式设计，支持移动端
- ⬅️➡️ 上一章/下一章导航
- ⌨️ 键盘快捷键支持

## 本地开发

### 前置要求

- Ruby 2.5.0或更高版本
- Bundler gem

### 安装步骤

1. 安装依赖：
```bash
bundle install
```

2. 启动本地服务器：
```bash
bundle exec jekyll serve
```

3. 在浏览器中访问：http://localhost:4000

## 项目结构

```
hly/
├── _config.yml          # Jekyll配置
├── index.html           # 首页（章节目录）
├── _layouts/            # 布局模板
├── _includes/           # 包含文件
├── assets/              # 静态资源（CSS、JS）
└── chapters/            # 章节文件
```

## 章节说明

- 总章节数：100章
- 实际章节：93章
- 缺失章节：7章（第17、22、23、32、88、90、91章）

缺失章节已标记为"本章节在原文档中缺失"。

## 技术栈

- Jekyll - 静态站点生成器
- GitHub Pages - 免费托管
- Markdown - 内容格式

## 许可证

本项目仅供学习交流使用。

---

**最后更新**: 2026-02-06
