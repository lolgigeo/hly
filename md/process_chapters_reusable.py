#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可复用的章节处理脚本

基于SOP标准和实际处理经验，提供完整的章节处理功能。
适用于类似项目的章节提取和Markdown生成。

使用方法：
    python3 md/process_chapters_reusable.py --start 1 --end 100
    python3 md/process_chapters_reusable.py --batch 1  # 处理批次1（11-20章）
    python3 md/process_chapters_reusable.py --chapter 3  # 处理单个章节
"""

import os
import re
import json
import argparse
from datetime import datetime
from pathlib import Path


# ==================== 配置 ====================

# 中文数字到阿拉伯数字的映射
CHINESE_DIGITS = {
    '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
    '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
    '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
    '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
    '二十一': 21, '二十二': 22, '二十三': 23, '二十四': 24, '二十五': 25,
    '二十六': 26, '二十七': 27, '二十八': 28, '二十九': 29, '三十': 30,
    '三十一': 31, '三十二': 32, '三十三': 33, '三十四': 34, '三十五': 35,
    '三十六': 36, '三十七': 37, '三十八': 38, '三十九': 39, '四十': 40,
    '四十一': 41, '四十二': 42, '四十三': 43, '四十四': 44, '四十五': 45,
    '四十六': 46, '四十七': 47, '四十八': 48, '四十九': 49, '五十': 50,
    '五十一': 51, '五十二': 52, '五十三': 53, '五十四': 54, '五十五': 55,
    '五十六': 56, '五十七': 57, '五十八': 58, '五十九': 59, '六十': 60,
    '六十一': 61, '六十二': 62, '六十三': 63, '六十四': 64, '六十五': 65,
    '六十六': 66, '六十七': 67, '六十八': 68, '六十九': 69, '七十': 70,
    '七十一': 71, '七十二': 72, '七十三': 73, '七十四': 74, '七十五': 75,
    '七十六': 76, '七十七': 77, '七十八': 78, '七十九': 79, '八十': 80,
    '八十一': 81, '八十二': 82, '八十三': 83, '八十四': 84, '八十五': 85,
    '八十六': 86, '八十七': 87, '八十八': 88, '八十九': 89, '九十': 90,
    '九十一': 91, '九十二': 92, '九十三': 93, '九十四': 94, '九十五': 95,
    '九十六': 96, '九十七': 97, '九十八': 98, '九十九': 99, '一百': 100
}

# 段落格式化参数
PARAGRAPH_MIN_LENGTH = 100  # 当前段落最小长度（字符）
NEXT_SENTENCE_MIN_LENGTH = 20  # 下一句最小长度（字符）

# 缺失章节识别参数
MISSING_CHAPTER_MAX_SIZE = 100  # 缺失章节最大文件大小（字节）


# ==================== 工具函数 ====================

def chinese_to_arabic(chinese_num):
    """将中文数字转换为阿拉伯数字"""
    return CHINESE_DIGITS.get(chinese_num, None)


def normalize_chapter_number(chapter_str):
    """标准化章节号：将中文数字或阿拉伯数字统一转换为阿拉伯数字"""
    if chapter_str.isdigit():
        return int(chapter_str)
    arabic = chinese_to_arabic(chapter_str)
    if arabic is not None:
        return arabic
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
        print(f"错误：读取章节{chapter_num}失败：{e}")
        return None


# ==================== 核心处理函数 ====================

def format_chapter_content_sop(content, chapter_num):
    """
    按照SOP标准格式化章节内容
    
    这是核心处理函数，实现了完整的章节格式化逻辑：
    1. 移除论坛信息
    2. 移除章节标记
    3. 移除副标题（带括号和无括号）
    4. 清理特殊字符和日期
    5. 智能段落格式化
    """
    lines = content.split('\n')
    filtered = []
    skip_next_chapter = False
    start_processing = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        if skip_next_chapter:
            break
        
        if not stripped:
            if start_processing:
                filtered.append('')
            continue
        
        # 1. 移除论坛信息（优先处理）
        if re.search(r'级别:|发帖:|Posted:|\[.*楼\]|堂中威望|贡献值|注册时间|最后登录|梦中的王子', stripped):
            chapter_match = re.search(r'第([0-9一二三四五六七八九十百]+)[回章]', stripped)
            if chapter_match:
                chapter_str = chapter_match.group(1)
                normalized = normalize_chapter_number(chapter_str)
                if normalized == chapter_num:
                    start_processing = True
                    # 移除论坛信息和章节标记
                    remaining = re.sub(r'级别:.*?注册时间.*?最后登录.*?\s*', '', stripped)
                    remaining = re.sub(r'第[0-9一二三四五六七八九十百]+[回章]\s*', '', remaining)
                    remaining = remaining.replace('?', '').strip()
                    remaining = re.sub(r':\d{4}-\d{2}-\d{2}\s*', '', remaining)
                    
                    # 处理副标题和正文在同一行的情况
                    # 先尝试匹配带括号的副标题
                    subtitle_match = re.match(r'^([^。，！？]*[（(].*?[）)])\s+(.+)$', remaining)
                    if subtitle_match:
                        remaining = subtitle_match.group(2).strip()
                    elif re.match(r'^[^。，！？]*[（(].*?[）)]$', remaining) and len(remaining) < 50:
                        continue
                    else:
                        # 处理无括号的副标题（如"温柔仙乡"、"绝代魔姬"）
                        simple_subtitle_match = re.match(r'^([^。，！？]{2,10})\s+(.+)$', remaining)
                        if simple_subtitle_match:
                            subtitle_part = simple_subtitle_match.group(1)
                            body_part = simple_subtitle_match.group(2)
                            if len(subtitle_part) <= 10 and len(body_part) > 20:
                                remaining = body_part.strip()
                    
                    remaining = re.sub(r'第[0-9一二三四五六七八九十百]+[回章]\s*', '', remaining)
                    if remaining:
                        filtered.append(remaining)
            continue
        
        # 2. 检查章节标记（其他章节）
        chapter_match = re.search(r'第([0-9一二三四五六七八九十百]+)[回章]', stripped)
        if chapter_match:
            chapter_str = chapter_match.group(1)
            normalized = normalize_chapter_number(chapter_str)
            if normalized == chapter_num:
                start_processing = True
                remaining = re.sub(r'第[0-9一二三四五六七八九十百]+[回章]\s*', '', stripped)
                remaining = remaining.replace('?', '').strip()
                remaining = re.sub(r':\d{4}-\d{2}-\d{2}\s*', '', remaining)
                
                subtitle_match = re.match(r'^([^。，！？]*[（(].*?[）)])\s+(.+)$', remaining)
                if subtitle_match:
                    remaining = subtitle_match.group(2).strip()
                elif re.match(r'^[^。，！？]*[（(].*?[）)]$', remaining) and len(remaining) < 50:
                    continue
                else:
                    simple_subtitle_match = re.match(r'^([^。，！？]{2,10})\s+(.+)$', remaining)
                    if simple_subtitle_match:
                        subtitle_part = simple_subtitle_match.group(1)
                        body_part = simple_subtitle_match.group(2)
                        if len(subtitle_part) <= 10 and len(body_part) > 20:
                            remaining = body_part.strip()
                
                remaining = re.sub(r'第[0-9一二三四五六七八九十百]+[回章]\s*', '', remaining)
                if remaining:
                    filtered.append(remaining)
                continue
            else:
                if start_processing:
                    skip_next_chapter = True
                    break
                continue
        
        # 3. 如果第一行没有章节标记，但有副标题和正文，直接处理
        if i == 0 and not start_processing:
            start_processing = True
            subtitle_match = re.match(r'^([^。，！？]*[（(].*?[）)])\s+(.+)$', stripped)
            if subtitle_match:
                body_text = subtitle_match.group(2).strip()
                body_text = re.sub(r'第[0-9一二三四五六七八九十百]+[回章]\s*', '', body_text)
                body_text = re.sub(r':\d{4}-\d{2}-\d{2}\s*', '', body_text)
                if body_text:
                    filtered.append(body_text)
                continue
            
            simple_subtitle_match = re.match(r'^([^。，！？]{2,10})\s+(.+)$', stripped)
            if simple_subtitle_match:
                subtitle_part = simple_subtitle_match.group(1)
                body_part = simple_subtitle_match.group(2)
                if len(subtitle_part) <= 10 and len(body_part) > 20:
                    body_text = body_part.strip()
                    body_text = re.sub(r'第[0-9一二三四五六七八九十百]+[回章]\s*', '', body_text)
                    body_text = re.sub(r':\d{4}-\d{2}-\d{2}\s*', '', body_text)
                    if body_text:
                        filtered.append(body_text)
                        continue
            
            cleaned = re.sub(r'第[0-9一二三四五六七八九十百]+[回章]\s*', '', stripped)
            cleaned = re.sub(r':\d{4}-\d{2}-\d{2}\s*', '', cleaned)
            if cleaned:
                filtered.append(cleaned)
            continue
        
        if not start_processing:
            continue
        
        # 4. 移除副标题（单独行）
        if re.match(r'^[^。，！？]*[（(].*?[）)]$', stripped) and len(stripped) < 50:
            continue
        
        # 5. 处理副标题与正文同行的情况
        subtitle_match = re.match(r'^([^。，！？]*[（(].*?[）)])\s+(.+)$', stripped)
        if subtitle_match:
            body_text = subtitle_match.group(2).strip()
            body_text = re.sub(r'第[0-9一二三四五六七八九十百]+[回章]\s*', '', body_text)
            body_text = re.sub(r':\d{4}-\d{2}-\d{2}\s*', '', body_text)
            if body_text:
                filtered.append(body_text)
            continue
        
        # 6. 移除单独的副标题
        if re.match(r'^[^。，！？]+$', stripped) and len(stripped) < 20 and not stripped.endswith(('。', '！', '？')):
            continue
        
        if stripped == '?':
            continue
        if stripped.startswith('?'):
            stripped = stripped[1:].strip()
        stripped = stripped.replace('窗体底端', '').strip()
        stripped = re.sub(r'第[0-9一二三四五六七八九十百]+[回章]\s*', '', stripped)
        stripped = re.sub(r':\d{4}-\d{2}-\d{2}\s*', '', stripped)
        
        if stripped:
            filtered.append(stripped)
    
    # 段落格式化：按照第01、02章的标准，段落之间一个空行
    full_text = ' '.join(filtered)
    
    # 再次确保移除所有章节标记（包括正文中的）
    full_text = re.sub(r'第[0-9一二三四五六七八九十百]+[回章]\s*', '', full_text)
    full_text = re.sub(r':\d{4}-\d{2}-\d{2}\s*', '', full_text)
    full_text = re.sub(r'\s+', ' ', full_text)
    
    # 改进的段落分割逻辑：参考第01章的格式
    parts = re.split(r'([。！？])', full_text)
    paragraphs = []
    current_para = []
    
    i = 0
    while i < len(parts):
        if i < len(parts) and parts[i].strip():
            sentence = parts[i]
            if i + 1 < len(parts):
                sentence += parts[i + 1]
            sentence = sentence.strip()
            
            if sentence:
                current_para.append(sentence)
                if sentence.endswith(('。', '！', '？')):
                    if i + 2 < len(parts):
                        next_part = parts[i + 2]
                        if i + 3 < len(parts):
                            next_part += parts[i + 3]
                        next_sentence = next_part.strip()
                        current_para_text = ' '.join(current_para)
                        if len(next_sentence) > NEXT_SENTENCE_MIN_LENGTH and len(current_para_text) > PARAGRAPH_MIN_LENGTH:
                            para_text = ' '.join(current_para)
                            if para_text.strip():
                                paragraphs.append(para_text.strip())
                            current_para = []
                    else:
                        para_text = ' '.join(current_para)
                        if para_text.strip():
                            paragraphs.append(para_text.strip())
                        current_para = []
        i += 2
    
    if current_para:
        para_text = ' '.join(current_para)
        if para_text.strip():
            paragraphs.append(para_text.strip())
    
    return '\n\n'.join(paragraphs).strip()


def generate_markdown(chapter_num, formatted_content):
    """生成Markdown内容"""
    if not formatted_content.strip():
        return f"# 第{chapter_num}章\n\n本章节内容为空。"
    
    return f"# 第{chapter_num}章\n\n{formatted_content}"


def generate_placeholder(chapter_num, result_dir='result'):
    """生成缺失章节的占位文件"""
    md_content = f"# 第{chapter_num}章\n\n本章节在原文档中缺失。"
    
    os.makedirs(result_dir, exist_ok=True)
    output_file = os.path.join(result_dir, f"第{chapter_num:02d}章.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return True


def process_chapter_sop(chapter_num, chapters_raw_dir='chapters_raw', result_dir='result'):
    """按照SOP标准处理单个章节"""
    # 读取章节内容
    content = read_chapter_content(chapter_num, chapters_raw_dir)
    
    if not content or not content.strip():
        print(f"✗ 第{chapter_num}章 内容为空或缺失")
        return False
    
    # 检查是否是占位文件（内容很少且只有论坛信息）
    if len(content.strip()) < MISSING_CHAPTER_MAX_SIZE and re.search(r'Posted:|\[.*楼\]|梦中的王子', content) and not re.search(r'第([0-9一二三四五六七八九十百]+)[回章]', content):
        return generate_placeholder(chapter_num, result_dir)
    
    # 格式化内容
    formatted_content = format_chapter_content_sop(content, chapter_num)
    
    # 如果格式化后内容为空，生成占位文件
    if not formatted_content.strip() or formatted_content.strip() == "本章节内容为空。":
        return generate_placeholder(chapter_num, result_dir)
    
    # 生成Markdown
    md_content = generate_markdown(chapter_num, formatted_content)
    
    # 创建输出目录
    os.makedirs(result_dir, exist_ok=True)
    
    # 保存Markdown文件
    output_file = os.path.join(result_dir, f"第{chapter_num:02d}章.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return True


# ==================== 批量处理 ====================

def process_batch(start_chapter, end_chapter, missing_chapters=None, chapters_raw_dir='chapters_raw', result_dir='result'):
    """批量处理章节"""
    if missing_chapters is None:
        missing_chapters = []
    
    print("=" * 60)
    print(f"开始处理第{start_chapter}-{end_chapter}章")
    print("=" * 60)
    
    success_count = 0
    placeholder_count = 0
    fail_count = 0
    
    for i in range(start_chapter, end_chapter + 1):
        if i in missing_chapters:
            if generate_placeholder(i, result_dir):
                print(f"✓ 第{i}章 已生成占位文件（缺失章节）")
                placeholder_count += 1
        else:
            if process_chapter_sop(i, chapters_raw_dir, result_dir):
                print(f"✓ 第{i}章 已按SOP标准处理完成")
                success_count += 1
            else:
                print(f"✗ 第{i}章 处理失败")
                fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"批次处理完成！")
    print(f"成功: {success_count}章 | 占位: {placeholder_count}章 | 失败: {fail_count}章")
    print("=" * 60)
    
    return success_count, placeholder_count, fail_count


# ==================== 命令行接口 ====================

def main():
    parser = argparse.ArgumentParser(description='可复用的章节处理脚本')
    parser.add_argument('--start', type=int, help='起始章节号')
    parser.add_argument('--end', type=int, help='结束章节号')
    parser.add_argument('--chapter', type=int, help='处理单个章节')
    parser.add_argument('--batch', type=int, help='处理指定批次（1-9）')
    parser.add_argument('--missing', nargs='+', type=int, help='缺失章节列表')
    parser.add_argument('--chapters-dir', default='chapters_raw', help='原始章节目录')
    parser.add_argument('--result-dir', default='result', help='输出目录')
    
    args = parser.parse_args()
    
    # 批次定义
    batches = {
        1: (11, 20, [17]),
        2: (21, 30, [22, 23]),
        3: (31, 40, [32]),
        4: (41, 50, []),
        5: (51, 60, []),
        6: (61, 70, []),
        7: (71, 80, []),
        8: (81, 90, [88, 90]),
        9: (91, 100, [91]),
    }
    
    if args.chapter:
        # 处理单个章节
        process_chapter_sop(args.chapter, args.chapters_dir, args.result_dir)
    elif args.batch:
        # 处理指定批次
        if args.batch in batches:
            start, end, missing = batches[args.batch]
            process_batch(start, end, missing, args.chapters_dir, args.result_dir)
        else:
            print(f"错误：批次{args.batch}不存在（有效范围：1-9）")
    elif args.start and args.end:
        # 处理指定范围
        missing = args.missing if args.missing else []
        process_batch(args.start, args.end, missing, args.chapters_dir, args.result_dir)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
