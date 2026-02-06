#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
章节分析脚本
识别hl.txt中所有格式的章节标记，并生成详细报告和配置文件
"""

import re
import json
from collections import defaultdict

def chinese_to_arabic(chinese_num):
    """
    将中文数字转换为阿拉伯数字
    支持：一、二、三...十、十一...二十、三十...一百
    """
    # 基础数字映射
    char_map = {
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
        '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
        '零': 0, '百': 100
    }
    
    if not chinese_num:
        return None
    
    # 处理"一百"
    if chinese_num == '一百':
        return 100
    
    # 处理"十X"格式（十一到十九）
    if chinese_num.startswith('十') and len(chinese_num) == 2:
        return 10 + char_map.get(chinese_num[1], 0)
    
    # 处理"X十"格式（二十、三十...九十）
    if chinese_num.endswith('十') and len(chinese_num) == 2:
        return char_map.get(chinese_num[0], 0) * 10
    
    # 处理"X十Y"格式（二十一、三十九等）
    if '十' in chinese_num and len(chinese_num) == 3:
        tens = char_map.get(chinese_num[0], 0)
        ones = char_map.get(chinese_num[2], 0)
        return tens * 10 + ones
    
    # 处理单个数字（一到九）
    if len(chinese_num) == 1:
        return char_map.get(chinese_num, None)
    
    return None

def extract_chapter_number(match_text):
    """
    从章节标记中提取章节编号
    返回：(统一编号, 原始格式)
    """
    # 提取数字部分
    arabic_match = re.search(r'第(\d+)', match_text)
    if arabic_match:
        num = int(arabic_match.group(1))
        return num, match_text
    
    # 提取中文数字部分
    chinese_match = re.search(r'第([一二三四五六七八九十百]+)', match_text)
    if chinese_match:
        chinese_num = chinese_match.group(1)
        num = chinese_to_arabic(chinese_num)
        if num is not None:
            return num, match_text
    
    return None, match_text

def find_chapters(input_file):
    """
    查找文件中所有章节标记
    返回：章节列表，每个元素包含(行号, 原始标记, 统一编号)
    """
    chapters = []
    
    # 定义所有可能的章节标记模式
    patterns = [
        (r'第\d+回', '阿拉伯数字+回'),
        (r'第[一二三四五六七八九十百]+回', '中文数字+回'),
        (r'第\d+章', '阿拉伯数字+章'),
        (r'第[一二三四五六七八九十百]+章', '中文数字+章'),
    ]
    
    try:
        with open(input_file, 'r', encoding='gbk', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                for pattern, pattern_type in patterns:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        match_text = match.group(0)
                        chapter_num, original_format = extract_chapter_number(match_text)
                        
                        if chapter_num is not None:
                            chapters.append({
                                'line': line_num,
                                'original': match_text,
                                'number': chapter_num,
                                'pattern_type': pattern_type,
                                'line_content': line.strip()[:100]  # 保存前100个字符作为上下文
                            })
                            break  # 每行只记录第一个匹配
                    if any(re.finditer(pattern, line)):
                        break  # 如果找到匹配，不再尝试其他模式
    
    except Exception as e:
        print(f"读取文件失败: {e}")
        return []
    
    # 按行号排序
    chapters.sort(key=lambda x: x['line'])
    
    return chapters

def analyze_chapters(chapters):
    """
    分析章节数据，生成统计信息
    """
    stats = {
        'total': len(chapters),
        'by_pattern': defaultdict(int),
        'by_number': {},
        'missing_numbers': [],
        'duplicates': []
    }
    
    # 统计各格式的数量
    for ch in chapters:
        stats['by_pattern'][ch['pattern_type']] += 1
        stats['by_number'][ch['number']] = ch
    
    # 找出缺失的章节编号
    if chapters:
        min_num = min(ch['number'] for ch in chapters)
        max_num = max(ch['number'] for ch in chapters)
        
        all_numbers = set(range(min_num, max_num + 1))
        found_numbers = set(ch['number'] for ch in chapters)
        stats['missing_numbers'] = sorted(all_numbers - found_numbers)
    
    # 找出重复的章节编号
    number_counts = defaultdict(list)
    for ch in chapters:
        number_counts[ch['number']].append(ch)
    
    stats['duplicates'] = {
        num: items for num, items in number_counts.items() if len(items) > 1
    }
    
    return stats

def generate_report(chapters, stats, output_file):
    """
    生成Markdown格式的分析报告
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 章节分析报告\n\n")
        f.write(f"生成时间：{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 统计摘要\n\n")
        f.write(f"- **总章节数**：{stats['total']}\n")
        f.write(f"- **编号范围**：{min(ch['number'] for ch in chapters) if chapters else 0} - {max(ch['number'] for ch in chapters) if chapters else 0}\n")
        f.write(f"- **缺失章节数**：{len(stats['missing_numbers'])}\n")
        f.write(f"- **重复章节数**：{len(stats['duplicates'])}\n\n")
        
        f.write("## 格式统计\n\n")
        for pattern_type, count in sorted(stats['by_pattern'].items()):
            f.write(f"- **{pattern_type}**：{count} 个\n")
        f.write("\n")
        
        if stats['missing_numbers']:
            f.write("## 缺失的章节编号\n\n")
            f.write(", ".join(f"第{num}回" for num in stats['missing_numbers'][:20]))
            if len(stats['missing_numbers']) > 20:
                f.write(f" ... (共{len(stats['missing_numbers'])}个)")
            f.write("\n\n")
        
        if stats['duplicates']:
            f.write("## 重复的章节编号\n\n")
            for num, items in sorted(stats['duplicates'].items()):
                f.write(f"- **第{num}回**：出现在 {len(items)} 处\n")
                for item in items:
                    f.write(f"  - 行 {item['line']}: {item['original']}\n")
            f.write("\n")
        
        f.write("## 详细章节列表\n\n")
        f.write("| 行号 | 统一编号 | 原始标记 | 格式类型 | 上下文预览 |\n")
        f.write("|------|----------|----------|----------|------------|\n")
        
        for ch in chapters:
            context = ch['line_content'].replace('|', '\\|')[:50]
            f.write(f"| {ch['line']} | 第{ch['number']}回 | {ch['original']} | {ch['pattern_type']} | {context}... |\n")

def generate_config(chapters, output_file):
    """
    生成JSON格式的章节配置文件
    """
    config = {
        'total_chapters': len(chapters),
        'chapters': []
    }
    
    # 为每个章节计算结束行号
    for i, ch in enumerate(chapters):
        start_line = ch['line']
        end_line = chapters[i + 1]['line'] - 1 if i + 1 < len(chapters) else None
        
        config['chapters'].append({
            'number': ch['number'],
            'original': ch['original'],
            'pattern_type': ch['pattern_type'],
            'start_line': start_line,
            'end_line': end_line
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def main():
    input_file = 'hl.txt'
    report_file = 'chapter_analysis_report.md'
    config_file = 'chapters_config.json'
    
    print("=" * 60)
    print("章节分析脚本")
    print("=" * 60)
    print(f"\n正在分析文件: {input_file}")
    
    # 查找所有章节
    chapters = find_chapters(input_file)
    
    if not chapters:
        print("未找到任何章节标记！")
        return
    
    print(f"\n找到 {len(chapters)} 个章节标记")
    
    # 分析章节数据
    stats = analyze_chapters(chapters)
    
    # 输出统计信息
    print("\n" + "=" * 60)
    print("统计信息")
    print("=" * 60)
    print(f"总章节数: {stats['total']}")
    print(f"编号范围: {min(ch['number'] for ch in chapters)} - {max(ch['number'] for ch in chapters)}")
    print(f"\n格式分布:")
    for pattern_type, count in sorted(stats['by_pattern'].items()):
        print(f"  {pattern_type}: {count} 个")
    
    if stats['missing_numbers']:
        print(f"\n缺失章节数: {len(stats['missing_numbers'])}")
        print(f"缺失章节: {', '.join(f'第{n}回' for n in stats['missing_numbers'][:10])}")
        if len(stats['missing_numbers']) > 10:
            print(f"  ... (共{len(stats['missing_numbers'])}个)")
    
    if stats['duplicates']:
        print(f"\n重复章节数: {len(stats['duplicates'])}")
        for num, items in list(stats['duplicates'].items())[:5]:
            print(f"  第{num}回: 出现在 {len(items)} 处")
    
    # 生成报告
    print(f"\n正在生成报告: {report_file}")
    generate_report(chapters, stats, report_file)
    print("报告生成完成！")
    
    # 生成配置文件
    print(f"\n正在生成配置文件: {config_file}")
    generate_config(chapters, config_file)
    print("配置文件生成完成！")
    
    print("\n" + "=" * 60)
    print("分析完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
