# GitHub Pages 设置说明

## ✅ 已完成的工作

1. ✅ 创建了完整的Jekyll项目结构
2. ✅ 100个章节文件已添加到`chapters/`目录
3. ✅ 所有文件已推送到GitHub仓库：https://github.com/lolgigeo/hly

## 📋 下一步：启用GitHub Pages

### 方法1：通过GitHub网页界面（推荐）

1. 访问仓库：https://github.com/lolgigeo/hly
2. 点击仓库右上角的 **Settings**（设置）
3. 在左侧菜单中找到 **Pages**（页面）
4. 在 **Source**（源）部分：
   - 选择 **Deploy from a branch**（从分支部署）
   - **Branch**（分支）：选择 `main`
   - **Folder**（文件夹）：选择 `/ (root)`
5. 点击 **Save**（保存）

### 方法2：通过GitHub Actions（可选）

如果需要自定义构建流程，可以创建`.github/workflows/pages.yml`文件。

## ⏱️ 部署时间

- 首次部署：通常需要5-10分钟
- 后续更新：通常需要1-3分钟

## 🌐 访问地址

部署完成后，您的网站将在以下地址可用：

**https://lolgigeo.github.io/hly/**

## 🔍 检查部署状态

1. 在仓库页面，点击 **Actions**（操作）标签
2. 查看最新的工作流运行状态
3. 如果显示绿色✓，表示部署成功

## 📝 功能特性

- ✅ 100个章节完整内容
- ✅ 章节搜索功能
- ✅ 响应式设计（移动端友好）
- ✅ 上一章/下一章导航
- ✅ 键盘快捷键支持（←上一章，→下一章，ESC返回目录）

## 🐛 故障排除

### 问题1：页面显示404

**解决方案**：
- 确认GitHub Pages已启用
- 等待5-10分钟让部署完成
- 检查仓库设置中的Pages配置

### 问题2：章节列表为空

**解决方案**：
- 确认`chapters/`目录下的文件都有正确的YAML front matter
- 检查`_config.yml`中的collections配置

### 问题3：样式未加载

**解决方案**：
- 确认`assets/css/style.css`文件存在
- 检查`_layouts/default.html`中的CSS引用路径

## 📞 需要帮助？

如果遇到问题，可以：
1. 检查GitHub Actions日志
2. 查看Jekyll文档：https://jekyllrb.com/docs/
3. 查看GitHub Pages文档：https://docs.github.com/en/pages

---

**最后更新**：2026-02-06
