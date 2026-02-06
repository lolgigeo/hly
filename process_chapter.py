#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单个章节处理辅助脚本
用于读取、显示和处理单个章节的内容
每次只处理一个章节，不进行批量处理
"""

import json
import os
import sys
from datetime import datetime

def load_progress(progress_file='progress.json'):
    """加载进度文件"""
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_progress(progress, progress_file='progress.json'):
    """保存进度文件"""
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def init_progress(config_file='chapters_config.json', progress_file='progress.json'):
    """初始化进度文件"""
    if os.path.exists(progress_file):
        print(f"进度文件已存在: {progress_file}")
        return
    
    config = load_chapters_config(config_file)
    if not config:
        print("无法加载章节配置")
        return
    
    chapters = config.get('chapters', [])
    progress = {}
    
    # 初始化所有章节（1-100）
    for num in range(1, 101):
        progress[str(num)] = {
            'status': 'pending',
            'created_at': None,
            'updated_at': None,
            'notes': ''
        }
    
    # 标记缺失章节
    found_numbers = {ch['number'] for ch in chapters}
    missing_numbers = set(range(1, 101)) - found_numbers
    
    for num in missing_numbers:
        progress[str(num)]['status'] = 'skipped'
        progress[str(num)]['notes'] = '原文档中缺失此章节'
    
    save_progress(progress, progress_file)
    print(f"已初始化进度文件: {progress_file}")
    print(f"总章节数: 100")
    print(f"待处理: {len(found_numbers)}")
    print(f"缺失章节: {len(missing_numbers)}")

def load_chapters_config(config_file):
    """加载章节配置"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        return None

def read_chapter_content(chapter_num, chapters_raw_dir='chapters_raw'):
    """读取章节原始内容"""
    filename = f"chapter_{chapter_num:02d}.txt"
    filepath = os.path.join(chapters_raw_dir, filename)
    
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取章节文件失败: {e}")
        return None

def display_chapter(chapter_num, content):
    """显示章节内容"""
    print("=" * 80)
    print(f"第 {chapter_num} 章")
    print("=" * 80)
    print()
    print(content[:2000])  # 显示前2000个字符
    if len(content) > 2000:
        print("\n... (内容已截断，完整内容请查看文件)")
    print()
    print("=" * 80)

def generate_markdown_template(chapter_num, content):
    """生成Markdown模板"""
    # 移除章节标记行（如果存在）
    lines = content.split('\n')
    filtered_lines = []
    skip_next = False
    
    for line in lines:
        # 跳过包含章节标记的行
        if any(marker in line for marker in ['第', '回', '章', 'Chapter']):
            if any(str(chapter_num) in line or f'{chapter_num:02d}' in line for _ in [1]):
                skip_next = True
                continue
        if skip_next and line.strip() == '':
            skip_next = False
            continue
        skip_next = False
        filtered_lines.append(line)
    
    # 生成Markdown
    md_content = f"# 第{chapter_num}章\n\n"
    md_content += '\n'.join(filtered_lines)
    
    return md_content

def process_chapter(chapter_num, chapters_raw_dir='chapters_raw', result_dir='result', progress_file='progress.json'):
    """处理单个章节"""
    # 加载进度
    progress = load_progress(progress_file)
    
    chapter_key = str(chapter_num)
    if chapter_key not in progress:
        print(f"错误: 章节 {chapter_num} 不在进度记录中")
        return False
    
    # 检查章节状态
    if progress[chapter_key]['status'] == 'completed':
        print(f"章节 {chapter_num} 已完成处理")
        response = input("是否重新处理？(y/n): ")
        if response.lower() != 'y':
            return False
    
    # 更新状态为处理中
    progress[chapter_key]['status'] = 'processing'
    progress[chapter_key]['updated_at'] = datetime.now().isoformat()
    save_progress(progress, progress_file)
    
    # 读取章节内容
    content = read_chapter_content(chapter_num, chapters_raw_dir)
    
    if not content:
        print(f"错误: 无法读取章节 {chapter_num} 的内容")
        progress[chapter_key]['status'] = 'error'
        progress[chapter_key]['notes'] = '无法读取内容'
        save_progress(progress, progress_file)
        return False
    
    # 显示章节内容
    display_chapter(chapter_num, content)
    
    # 生成Markdown模板
    md_content = generate_markdown_template(chapter_num, content)
    
    # 创建输出目录
    os.makedirs(result_dir, exist_ok=True)
    
    # 保存Markdown文件
    output_file = os.path.join(result_dir, f"第{chapter_num:02d}章.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"\nMarkdown文件已生成: {output_file}")
    print("\n请检查内容并进行必要的格式校对：")
    print("1. 检查段落格式")
    print("2. 检查标点符号")
    print("3. 检查章节标题")
    print("4. 检查特殊字符")
    
    # 等待用户确认
    response = input("\n校对完成后，是否标记为已完成？(y/n): ")
    if response.lower() == 'y':
        progress[chapter_key]['status'] = 'completed'
        progress[chapter_key]['updated_at'] = datetime.now().isoformat()
        if not progress[chapter_key]['created_at']:
            progress[chapter_key]['created_at'] = datetime.now().isoformat()
        save_progress(progress, progress_file)
        print(f"章节 {chapter_num} 已标记为完成")
    else:
        print(f"章节 {chapter_num} 保持为处理中状态")
    
    return True

def show_progress(progress_file='progress.json'):
    """显示处理进度"""
    progress = load_progress(progress_file)
    
    if not progress:
        print("进度文件不存在或为空")
        return
    
    total = len(progress)
    completed = sum(1 for p in progress.values() if p.get('status') == 'completed')
    processing = sum(1 for p in progress.values() if p.get('status') == 'processing')
    pending = sum(1 for p in progress.values() if p.get('status') == 'pending')
    skipped = sum(1 for p in progress.values() if p.get('status') == 'skipped')
    
    print("=" * 60)
    print("处理进度")
    print("=" * 60)
    print(f"总章节数: {total}")
    print(f"已完成: {completed}")
    print(f"处理中: {processing}")
    print(f"待处理: {pending}")
    print(f"已跳过: {skipped}")
    print(f"完成率: {completed/total*100:.1f}%")
    print("=" * 60)

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 process_chapter.py init                    # 初始化进度文件")
        print("  python3 process_chapter.py <章节号>                # 处理指定章节")
        print("  python3 process_chapter.py progress                # 显示进度")
        print("  python3 process_chapter.py next                    # 处理下一个待处理章节")
        print()
        print("示例:")
        print("  python3 process_chapter.py init")
        print("  python3 process_chapter.py 1")
        print("  python3 process_chapter.py progress")
        return
    
    command = sys.argv[1]
    
    if command == 'init':
        init_progress()
    elif command == 'progress':
        show_progress()
    elif command == 'next':
        progress = load_progress()
        if not progress:
            print("请先运行 'python3 process_chapter.py init' 初始化进度文件")
            return
        
        # 找到下一个待处理的章节
        for num in range(1, 101):
            chapter_key = str(num)
            if progress.get(chapter_key, {}).get('status') == 'pending':
                print(f"处理下一个章节: {num}")
                process_chapter(num)
                return
        
        print("所有章节都已处理完成或跳过")
    elif command.isdigit():
        chapter_num = int(command)
        if chapter_num < 1 or chapter_num > 100:
            print("章节号必须在 1-100 之间")
            return
        process_chapter(chapter_num)
    else:
        print(f"未知命令: {command}")

if __name__ == '__main__':
    main()
