#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 EPUB 电子书全集
从 chapters 目录读取所有章节文件，合并生成 EPUB 格式的电子书
"""

import os
import re
import yaml
import markdown
from datetime import datetime
from pathlib import Path

try:
    import ebooklib
    from ebooklib import epub
except ImportError:
    print("错误: 需要安装 ebooklib 库")
    print("请运行: pip install ebooklib markdown pyyaml")
    exit(1)


def parse_front_matter(content):
    """解析 Markdown 文件的 front matter"""
    # 检查是否有 front matter
    if not content.startswith('---'):
        return {}, content
    
    # 找到 front matter 的结束位置
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    
    front_matter_text = parts[1]
    body = parts[2]
    
    try:
        front_matter = yaml.safe_load(front_matter_text)
        if front_matter is None:
            front_matter = {}
    except:
        front_matter = {}
    
    return front_matter, body.strip()


def markdown_to_html(markdown_text):
    """将 Markdown 转换为 HTML"""
    md = markdown.Markdown(extensions=['extra', 'codehilite'])
    html = md.convert(markdown_text)
    return html


def get_chapter_files(chapters_dir):
    """获取所有章节文件，按章节号排序"""
    chapter_files = []
    
    for i in range(1, 101):
        # 尝试不同的文件名格式
        for fmt in [f"{i:02d}.md", f"{i}.md"]:
            file_path = os.path.join(chapters_dir, fmt)
            if os.path.exists(file_path):
                chapter_files.append((i, file_path))
                break
    
    return sorted(chapter_files, key=lambda x: x[0])


def create_epub(chapters_dir, output_file='hly_complete.epub'):
    """创建 EPUB 电子书"""
    
    # 创建 EPUB 书籍
    book = epub.EpubBook()
    
    # 设置元数据
    book.set_identifier('hly_complete_001')
    book.set_title('红楼遗秘')
    book.set_language('zh-CN')
    book.add_author('迷男')
    book.add_metadata('DC', 'description', '100章完整内容在线阅读')
    
    # 获取所有章节文件
    chapter_files = get_chapter_files(chapters_dir)
    
    if not chapter_files:
        print(f"错误: 在 {chapters_dir} 目录中未找到章节文件")
        return False
    
    print(f"找到 {len(chapter_files)} 个章节文件")
    
    # 存储所有章节
    chapters = []
    spine = ['nav']
    toc = []
    
    # 处理每个章节
    for chapter_num, file_path in chapter_files:
        print(f"处理章节 {chapter_num}: {os.path.basename(file_path)}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析 front matter 和内容
            front_matter, body = parse_front_matter(content)
            
            # 获取章节标题
            title = front_matter.get('title', f'第{chapter_num}章')
            
            # 检查是否是缺失章节
            if '缺失' in body or '本章节在原文档中缺失' in body:
                print(f"  跳过缺失章节: {title}")
                continue
            
            # 检查内容是否为空
            if not body.strip():
                print(f"  警告: 章节 {chapter_num} 内容为空，跳过")
                continue
            
            # 将 Markdown 转换为 HTML
            html_content = markdown_to_html(body)
            
            # 确保 HTML 内容不为空
            if not html_content.strip():
                html_content = "<p>（本章节内容为空）</p>"
            
            # 创建章节 HTML
            chapter_html = f"""<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{title}</title>
    <style>
        body {{
            font-family: "Microsoft YaHei", "SimSun", serif;
            font-size: 1.2em;
            line-height: 1.8;
            margin: 2em;
            text-align: justify;
        }}
        h1 {{
            font-size: 1.5em;
            text-align: center;
            margin-bottom: 1em;
            border-bottom: 2px solid #333;
            padding-bottom: 0.5em;
        }}
        p {{
            margin: 1em 0;
            text-indent: 2em;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    {html_content}
</body>
</html>"""
            
            # 创建 EPUB 章节
            chapter_id = f'chapter_{chapter_num:03d}'
            chapter = epub.EpubHtml(
                title=title,
                file_name=f'{chapter_id}.xhtml',
                lang='zh-CN'
            )
            chapter.content = chapter_html.encode('utf-8')
            
            # 添加到书籍
            book.add_item(chapter)
            chapters.append(chapter)
            spine.append(chapter)
            toc.append(epub.Section(title))
            toc.append(chapter)
            
        except Exception as e:
            print(f"  错误处理章节 {chapter_num}: {e}")
            continue
    
    if not chapters:
        print("错误: 没有有效的章节可以添加到 EPUB")
        return False
    
    # 设置目录
    book.toc = toc
    
    # 添加导航文件
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # 设置书籍结构
    book.spine = spine
    
    # 写入 EPUB 文件
    print(f"\n正在生成 EPUB 文件: {output_file}")
    epub.write_epub(output_file, book, {})
    
    print(f"✓ EPUB 文件已成功生成: {output_file}")
    print(f"  包含 {len(chapters)} 个章节")
    
    return True


def main():
    """主函数"""
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    chapters_dir = os.path.join(script_dir, 'chapters')
    output_file = os.path.join(script_dir, 'hly_complete.epub')
    
    # 检查 chapters 目录是否存在
    if not os.path.exists(chapters_dir):
        print(f"错误: 目录不存在: {chapters_dir}")
        return
    
    print("=" * 60)
    print("EPUB 电子书生成工具")
    print("=" * 60)
    print(f"章节目录: {chapters_dir}")
    print(f"输出文件: {output_file}")
    print()
    
    # 创建 EPUB
    if create_epub(chapters_dir, output_file):
        print("\n生成完成！")
    else:
        print("\n生成失败！")


if __name__ == '__main__':
    main()
