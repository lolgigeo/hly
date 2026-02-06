#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本清理脚本
清理hl.txt中的论坛格式信息、多余空白等，生成清理后的文本
"""

import re
import sys

def clean_text(input_file, output_file):
    """清理文本文件"""
    print(f"正在读取文件: {input_file}")
    
    # 读取GBK编码的文件
    try:
        with open(input_file, 'r', encoding='gbk', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        return False
    
    print(f"原始文件大小: {len(content)} 字符")
    
    # 1. 移除论坛格式信息（用户信息、发帖时间等）
    print("正在清理论坛格式信息...")
    
    # 移除包含"级别:"、"发帖:"、"Posted:"等论坛标记的行块
    # 匹配模式：从"级别:"开始到"第XX回"之前的所有内容
    content = re.sub(r'级别:.*?最后登录:\d+.*?(?=第\d+回|$)', '', content, flags=re.DOTALL)
    
    # 移除单独的"Posted: 日期"行
    content = re.sub(r'Posted:\s*\d{4}-\d{2}-\d{2}.*?\n', '', content)
    
    # 移除楼层号行（如"[107 楼]"）
    content = re.sub(r'\[\d+\s+楼\]\s*', '', content)
    
    # 移除用户签名块（通常包含多个空行和特殊字符）
    content = re.sub(r'\n{3,}.*?级别:.*?\n{3,}', '\n\n', content, flags=re.DOTALL)
    
    # 2. 清理多余的空白和换行
    print("正在清理多余空白...")
    
    # 统一换行符（Windows CRLF -> Unix LF）
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    
    # 移除行尾空白
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
    
    # 合并多个连续空行为最多两个空行（保留段落分隔）
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    # 3. 清理特殊字符和控制字符（保留中文标点和常用符号）
    print("正在清理特殊字符...")
    
    # 移除控制字符（保留换行符和制表符）
    content = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', content)
    
    # 4. 处理章节标记格式
    print("正在规范化章节标记...")
    
    # 确保章节标记前后有适当的空行
    # 在"第XX回"前确保有空行（如果前面不是空行）
    content = re.sub(r'([^\n])\n(第\d+回)', r'\1\n\n\2', content)
    
    # 如果章节标记后直接跟内容（没有换行），添加换行
    content = re.sub(r'(第\d+回\s+)([^\n])', r'\1\n\2', content)
    
    # 5. 移除文件开头和结尾的多余空行
    content = content.strip() + '\n'
    
    print(f"清理后文件大小: {len(content)} 字符")
    print(f"减少了: {len(content) - len(content)} 字符")
    
    # 写入清理后的文件
    print(f"正在写入文件: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("清理完成！")
        return True
    except Exception as e:
        print(f"写入文件失败: {e}")
        return False

def show_sample(input_file, output_file, lines=50):
    """显示清理前后的对比样本"""
    print("\n" + "="*60)
    print("清理前后对比（前50行）")
    print("="*60)
    
    # 读取原始文件样本
    try:
        with open(input_file, 'r', encoding='gbk', errors='ignore') as f:
            original_lines = [f.readline() for _ in range(lines)]
        original_sample = ''.join(original_lines)
    except:
        original_sample = "无法读取原始文件"
    
    # 读取清理后文件样本
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            cleaned_lines = [f.readline() for _ in range(lines)]
        cleaned_sample = ''.join(cleaned_lines)
    except:
        cleaned_sample = "清理后的文件尚未生成"
    
    print("\n【原始文本（前50行）】")
    print("-" * 60)
    print(original_sample)
    
    print("\n【清理后文本（前50行）】")
    print("-" * 60)
    print(cleaned_sample)
    
    print("\n" + "="*60)

if __name__ == '__main__':
    input_file = 'hl.txt'
    output_file = 'hl_cleaned.txt'
    
    if clean_text(input_file, output_file):
        show_sample(input_file, output_file)
    else:
        print("清理失败，请检查错误信息")
        sys.exit(1)
