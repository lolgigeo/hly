# 章节处理文档和工具使用指南

## 文档说明

本目录包含章节处理项目的完整文档和可复用工具：

### 📄 文档文件

1. **`sop.md`** - 标准操作程序
   - 完整的处理流程和规范
   - 基于第01-100章的实际处理经验
   - 包含常见问题解决方案

2. **`experience.md`** - 经验总结与教训
   - 详细的处理经验总结
   - 常见问题与解决方案
   - 最佳实践和技术要点

3. **`plan.md`** - 执行计划
   - 批次处理计划
   - 进度跟踪
   - 质量检查清单

### 🛠️ 工具文件

4. **`process_chapters_reusable.py`** - 可复用处理脚本
   - 基于SOP标准的完整处理逻辑
   - 支持单个章节、批量、批次处理
   - 可直接用于类似项目

---

## 快速开始

### 1. 处理单个章节

```bash
python3 md/process_chapters_reusable.py --chapter 3
```

### 2. 处理指定范围

```bash
python3 md/process_chapters_reusable.py --start 11 --end 20
```

### 3. 处理指定批次

```bash
python3 md/process_chapters_reusable.py --batch 1  # 处理批次1（11-20章）
```

### 4. 处理指定范围（含缺失章节）

```bash
python3 md/process_chapters_reusable.py --start 21 --end 30 --missing 22 23
```

---

## 完整处理流程

### 阶段1：文本清理

```bash
python3 clean_text.py
```

**输出**：`hl_cleaned.txt`（UTF-8编码）

### 阶段2：章节分析

```bash
python3 analyze_chapters.py
```

**输出**：
- `chapters_config.json` - 章节配置
- `chapter_analysis_report.md` - 分析报告

### 阶段3：批量提取章节

```bash
python3 extract_chapters.py
```

**输出**：`chapters_raw/chapter_XX.txt`（100个文件）

### 阶段4：批量处理章节

#### 方式1：使用可复用脚本（推荐）

```bash
# 处理批次1（11-20章）
python3 md/process_chapters_reusable.py --batch 1

# 处理所有批次
for i in {1..9}; do
    python3 md/process_chapters_reusable.py --batch $i
done
```

#### 方式2：使用内联Python脚本

参考`md/plan.md`中的处理脚本示例。

**输出**：`result/第XX章.md`（100个文件）

---

## 配置说明

### 处理参数配置

在`process_chapters_reusable.py`中可以调整以下参数：

```python
# 段落格式化参数
PARAGRAPH_MIN_LENGTH = 100  # 当前段落最小长度（字符）
NEXT_SENTENCE_MIN_LENGTH = 20  # 下一句最小长度（字符）

# 缺失章节识别参数
MISSING_CHAPTER_MAX_SIZE = 100  # 缺失章节最大文件大小（字节）
```

### 目录配置

```python
# 默认目录
chapters_raw_dir = 'chapters_raw'  # 原始章节目录
result_dir = 'result'  # 输出目录
```

可以通过命令行参数修改：

```bash
python3 md/process_chapters_reusable.py --batch 1 \
    --chapters-dir custom_chapters \
    --result-dir custom_result
```

---

## 质量检查

### 自动检查清单

处理完成后，使用以下命令检查：

```bash
# 检查文件数量
ls result/第*.md | wc -l  # 应该输出100

# 检查缺失章节
grep -l "缺失" result/第*.md | wc -l  # 应该输出7

# 检查文件命名
ls result/第*.md | head -5  # 应该看到：第01章.md, 第02章.md...
```

### 手动检查清单

参考`md/sop.md`第5.3节的质量检查清单：

- [ ] 标题格式：`# 第X章`（不补零）
- [ ] 副标题已移除
- [ ] 章节标记已清理
- [ ] 论坛信息已清理
- [ ] 段落格式统一（段落之间一个空行）
- [ ] 特殊字符已移除
- [ ] 编码正确（UTF-8）
- [ ] 内容完整，无截断

---

## 常见问题

### Q1: 如何处理缺失章节？

缺失章节会自动识别并生成占位文件。如果需要手动指定：

```bash
python3 md/process_chapters_reusable.py --start 21 --end 30 --missing 22 23
```

### Q2: 如何调整段落格式参数？

编辑`process_chapters_reusable.py`中的参数：

```python
PARAGRAPH_MIN_LENGTH = 100  # 调整为其他值
NEXT_SENTENCE_MIN_LENGTH = 20  # 调整为其他值
```

### Q3: 如何处理其他格式的章节标记？

在`process_chapters_reusable.py`中扩展`CHINESE_DIGITS`字典，添加新的中文数字映射。

### Q4: 如何验证处理结果？

参考`md/experience.md`第6节的项目统计部分，使用提供的验证命令。

---

## 文档结构

```
md/
├── README.md                      # 本文档（使用指南）
├── sop.md                         # 标准操作程序（v2.0）
├── experience.md                  # 经验总结与教训
├── plan.md                        # 执行计划
└── process_chapters_reusable.py   # 可复用处理脚本
```

---

## 版本历史

- **v2.0** (2026-02-06)
  - 更新SOP，加入实际处理中的问题和解决方案
  - 创建经验总结文档
  - 创建可复用处理脚本
  - 基于100章完整处理经验

- **v1.0** (2026-02-06)
  - 初始版本
  - 基于第01、02章处理经验

---

## 参考资源

- **SOP文档**：`md/sop.md` - 完整的处理流程和规范
- **经验总结**：`md/experience.md` - 详细的处理经验和教训
- **执行计划**：`md/plan.md` - 批次处理计划和进度跟踪

---

**最后更新**：2026-02-06  
**维护者**：AI Assistant
