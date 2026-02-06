#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量提取章节脚本
从hl_cleaned.txt中提取所有章节的原始内容，保存到chapters_raw目录
"""

import json
import os
from pathlib import Path

def load_chapters_config(config_file):
    """加载章节配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        return None

def extract_chapter_content(input_file, start_line, end_line, encoding='utf-8'):
    """
    从输入文件中提取指定行号范围的内容
    """
    try:
        with open(input_file, 'r', encoding=encoding, errors='ignore') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        
        # 行号从1开始，数组索引从0开始
        start_idx = max(0, start_line - 1)
        
        # 处理end_line为None的情况（最后一个章节）
        if end_line is None:
            end_idx = total_lines
        else:
            # end_line是下一章节的开始行，所以当前章节应该到end_line-1
            end_idx = min(end_line - 1, total_lines)
        
        # 确保索引有效
        if start_idx >= end_idx:
            print(f"警告: 无效的行号范围 {start_line}-{end_line} (文件总行数: {total_lines})")
            return None
        
        # 提取内容（包含start_idx，不包含end_idx）
        content_lines = lines[start_idx:end_idx]
        return ''.join(content_lines)
    except Exception as e:
        print(f"提取章节内容失败 (行 {start_line}-{end_line}): {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_all_chapters(input_file, config_file, output_dir):
    """
    批量提取所有章节
    """
    # 加载配置
    config = load_chapters_config(config_file)
    if not config:
        return False
    
    chapters = config.get('chapters', [])
    if not chapters:
        print("配置文件中没有找到章节信息")
        return False
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成所有章节编号列表（1-100）
    all_chapter_numbers = set(range(1, 101))
    found_chapter_numbers = {ch['number'] for ch in chapters}
    missing_chapter_numbers = sorted(all_chapter_numbers - found_chapter_numbers)
    
    print(f"找到 {len(chapters)} 个章节")
    print(f"缺失章节: {missing_chapter_numbers}")
    
    # 确定文件编码
    encoding = 'gbk' if 'hl.txt' in input_file else 'utf-8'
    
    # 提取实际存在的章节
    extracted_count = 0
    for chapter in chapters:
        chapter_num = chapter['number']
        start_line = chapter['start_line']
        end_line = chapter['end_line']
        
        # 提取内容
        content = extract_chapter_content(input_file, start_line, end_line, encoding)
        
        if content:
            # 保存到文件
            filename = f"chapter_{chapter_num:02d}.txt"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            extracted_count += 1
            print(f"已提取: {filename} (行 {start_line}-{end_line})")
        else:
            print(f"提取失败: 第{chapter_num}章")
    
    # 为缺失章节创建占位文件
    for chapter_num in missing_chapter_numbers:
        filename = f"chapter_{chapter_num:02d}.txt"
        filepath = os.path.join(output_dir, filename)
        
        placeholder_content = f"本章节（第{chapter_num}章）在原文档中缺失。\n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(placeholder_content)
        
        print(f"已创建占位文件: {filename}")
    
    print(f"\n提取完成！共提取 {extracted_count} 个章节，创建 {len(missing_chapter_numbers)} 个占位文件")
    return True

def generate_chapters_list(config_file, output_file):
    """
    生成章节目录清单
    """
    config = load_chapters_config(config_file)
    if not config:
        return False
    
    chapters = config.get('chapters', [])
    
    # 按章节编号排序
    chapters_sorted = sorted(chapters, key=lambda x: x['number'])
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("章节目录清单\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"总章节数: {len(chapters)}\n")
            f.write(f"编号范围: {min(ch['number'] for ch in chapters)} - {max(ch['number'] for ch in chapters)}\n\n")
            
            f.write("章节列表:\n")
            f.write("-" * 60 + "\n")
            f.write(f"{'编号':<6} {'原始标记':<15} {'起始行':<10} {'结束行':<10} {'格式类型'}\n")
            f.write("-" * 60 + "\n")
            
            for ch in chapters_sorted:
                end_line_str = str(ch['end_line']) if ch['end_line'] else "文件末尾"
                f.write(f"{ch['number']:<6} {ch['original']:<15} {ch['start_line']:<10} {end_line_str:<10} {ch['pattern_type']}\n")
            
            # 列出缺失章节
            all_numbers = set(range(1, 101))
            found_numbers = {ch['number'] for ch in chapters}
            missing_numbers = sorted(all_numbers - found_numbers)
            
            if missing_numbers:
                f.write("\n缺失章节:\n")
                f.write("-" * 60 + "\n")
                for num in missing_numbers:
                    f.write(f"第{num}章\n")
        
        print(f"章节目录清单已生成: {output_file}")
        return True
    except Exception as e:
        print(f"生成章节目录清单失败: {e}")
        return False

def main():
    # 注意：章节配置中的行号是基于原始hl.txt文件的
    # 但我们可以从清理后的文件提取，需要先检查行号是否匹配
    input_file = 'hl_cleaned.txt'
    original_file = 'hl.txt'  # 备用：如果清理后的文件行数不匹配，使用原始文件
    config_file = 'chapters_config.json'
    output_dir = 'chapters_raw'
    list_file = 'chapters_list.txt'
    
    print("=" * 60)
    print("批量提取章节脚本")
    print("=" * 60)
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"警告: 清理后的文件不存在: {input_file}")
        if os.path.exists(original_file):
            print(f"使用原始文件: {original_file}")
            input_file = original_file
        else:
            print("错误: 找不到输入文件")
            return
    
    # 检查文件行数，如果清理后的文件行数太少，使用原始文件
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines_count = len(f.readlines())
    
    # 检查配置中的最大行号
    config = load_chapters_config(config_file)
    if config:
        max_line = max(ch.get('end_line', ch.get('start_line', 0)) or ch.get('start_line', 0) 
                      for ch in config.get('chapters', []))
        if max_line > lines_count:
            print(f"警告: 配置中的最大行号({max_line})超过文件行数({lines_count})")
            if os.path.exists(original_file):
                print(f"切换到原始文件: {original_file}")
                input_file = original_file
                # 重新读取文件行数
                with open(input_file, 'r', encoding='gbk', errors='ignore') as f:
                    lines_count = len(f.readlines())
                print(f"原始文件行数: {lines_count}")
    
    if not os.path.exists(config_file):
        print(f"错误: 配置文件不存在: {config_file}")
        print("请先运行 analyze_chapters.py 生成章节配置文件")
        return
    
    # 提取所有章节
    print(f"\n正在从 {input_file} 提取章节...")
    success = extract_all_chapters(input_file, config_file, output_dir)
    
    if success:
        # 生成章节目录清单
        print(f"\n正在生成章节目录清单...")
        generate_chapters_list(config_file, list_file)
        
        print("\n" + "=" * 60)
        print("提取完成！")
        print("=" * 60)
        print(f"输出目录: {output_dir}/")
        print(f"章节目录: {list_file}")
    else:
        print("\n提取失败，请检查错误信息")

if __name__ == '__main__':
    main()
