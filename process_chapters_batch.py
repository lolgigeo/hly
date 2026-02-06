#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理章节脚本（非交互模式）
逐个处理指定范围的章节，自动进行格式校对和Markdown生成
"""

import json
import os
import re
from datetime import datetime

def load_progress(progress_file='progress.json'):
    """加载进度文件"""
    with open(progress_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_progress(progress, progress_file='progress.json'):
    """保存进度文件"""
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def read_chapter_content(chapter_num, chapters_raw_dir='chapters_raw'):
    """读取章节原始内容"""
    filename = f"chapter_{chapter_num:02d}.txt"
    filepath = os.path.join(chapters_raw_dir, filename)
    
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def format_chapter_content(content, chapter_num):
    """格式化章节内容"""
    # 移除章节标记行和论坛信息
    lines = content.split('\n')
    filtered_lines = []
    
    # 跳过开头的论坛信息行
    skip_initial_forum = True
    
    for line in lines:
        # 跳过包含章节标记的行（但保留章节标题后的内容）
        # 只匹配行首或行中独立的章节标记（如"第03回"或"第3章"），不匹配括号中的内容
        chapter_marker = re.search(r'^第[0-9一二三四五六七八九十百]+[回章]|^第[0-9一二三四五六七八九十百]+[回章]\s', line)
        if chapter_marker:
            # 如果这行包含正确的章节号，跳过整行
            if re.search(rf'^第0?{chapter_num}[回章]|^第{chapter_num:02d}[回章]', line):
                skip_initial_forum = False
                continue
            # 如果包含其他章节号，说明是下一章的开始，停止处理
            else:
                break  # 遇到下一章标记，停止处理
        
        # 跳过论坛信息行（只在开头跳过）
        if skip_initial_forum:
            if re.search(r'级别:|发帖:|Posted:|\[.*楼\]|堂中威望|贡献值|注册时间|最后登录|梦中的王子', line):
                continue
        
        # 跳过空行和特殊字符行（但保留有内容的行）
        stripped = line.strip()
        if stripped == '' or stripped == '?':
            # 保留空行用于段落分隔
            if filtered_lines:  # 如果已有内容，保留空行
                filtered_lines.append('')
            continue
        
        # 如果行太短且不是有效内容，跳过
        if len(stripped) < 2:
            continue
        
        skip_initial_forum = False
        filtered_lines.append(line)
    
    # 合并内容
    text = '\n'.join(filtered_lines)
    
    # 如果内容为空，直接返回
    if not text.strip():
        return ''
    
    # 规范化段落：合并被错误分割的段落
    # 如果一行不以句号、问号、感叹号结尾，且下一行不是空行，则合并
    paragraphs = []
    current_para = []
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            if current_para:
                paragraphs.append(' '.join(current_para))
                current_para = []
        else:
            # 检查是否应该开始新段落
            if line and current_para:
                last_char = current_para[-1][-1] if current_para[-1] else ''
                if last_char in '。！？' and len(line) > 10:
                    paragraphs.append(' '.join(current_para))
                    current_para = [line]
                else:
                    current_para.append(line)
            else:
                current_para.append(line)
    
    if current_para:
        paragraphs.append(' '.join(current_para))
    
    # 规范化段落间距（两个空行）
    result = '\n\n'.join(paragraphs)
    return result if result.strip() else text.strip()  # 如果格式化后为空，返回原始文本

def generate_markdown(chapter_num, formatted_content):
    """生成Markdown内容"""
    md_content = f"# 第{chapter_num}章\n\n"
    md_content += formatted_content
    return md_content

def process_chapter(chapter_num, chapters_raw_dir='chapters_raw', result_dir='result', progress_file='progress.json'):
    """处理单个章节"""
    progress = load_progress(progress_file)
    chapter_key = str(chapter_num)
    
    if progress.get(chapter_key, {}).get('status') == 'completed':
        print(f"章节 {chapter_num} 已完成，跳过")
        return True
    
    # 更新状态为处理中
    progress[chapter_key]['status'] = 'processing'
    progress[chapter_key]['updated_at'] = datetime.now().isoformat()
    save_progress(progress, progress_file)
    
    # 读取章节内容
    content = read_chapter_content(chapter_num, chapters_raw_dir)
    
    if not content or content.strip().startswith('本章节'):
        print(f"章节 {chapter_num} 内容为空或缺失")
        progress[chapter_key]['status'] = 'skipped'
        progress[chapter_key]['notes'] = '内容为空或缺失'
        save_progress(progress, progress_file)
        return False
    
    # 格式化内容
    formatted_content = format_chapter_content(content, chapter_num)
    
    # 生成Markdown
    md_content = generate_markdown(chapter_num, formatted_content)
    
    # 创建输出目录
    os.makedirs(result_dir, exist_ok=True)
    
    # 保存Markdown文件
    output_file = os.path.join(result_dir, f"第{chapter_num:02d}章.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    # 更新进度
    progress[chapter_key]['status'] = 'completed'
    progress[chapter_key]['created_at'] = datetime.now().isoformat()
    progress[chapter_key]['updated_at'] = datetime.now().isoformat()
    progress[chapter_key]['notes'] = '已完成格式校对和Markdown生成'
    save_progress(progress, progress_file)
    
    print(f"✓ 第{chapter_num}章 处理完成")
    return True

def process_chapters_range(start, end, chapters_raw_dir='chapters_raw', result_dir='result', progress_file='progress.json'):
    """批量处理章节范围"""
    print(f"开始处理第{start}-{end}章...")
    print("=" * 60)
    
    success_count = 0
    skip_count = 0
    
    for chapter_num in range(start, end + 1):
        if process_chapter(chapter_num, chapters_raw_dir, result_dir, progress_file):
            success_count += 1
        else:
            skip_count += 1
    
    print("=" * 60)
    print(f"处理完成！成功: {success_count}, 跳过: {skip_count}")

def main():
    import sys
    
    if len(sys.argv) < 3:
        print("用法: python3 process_chapters_batch.py <起始章节> <结束章节>")
        print("示例: python3 process_chapters_batch.py 3 16")
        return
    
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    
    process_chapters_range(start, end)

if __name__ == '__main__':
    main()
