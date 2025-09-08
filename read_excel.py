#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import requests
import json
import os

def read_excel_data():
    """读取Excel文件的所有行数据"""
    try:
        # 读取Excel文件
        df = pd.read_excel('/Users/lizhuang/Desktop/Model/text-to-speech/音频缺少数据_cleaned.xlsx')
        
        print("Excel文件列名:")
        print(df.columns.tolist())
        print(f"\n总共有 {len(df)} 行数据")
        
        # 显示所有行的C、E、F、G、H、I、J列
        columns_to_check = ['C', 'E', 'F', 'G', 'H', 'I', 'J']
        
        # 如果列名不是字母，尝试使用索引
        if 'C' not in df.columns:
            # 使用列索引 (C=2, E=4, F=5, G=6, H=7, I=8, J=9)
            df_subset = df.iloc[:, [2, 4, 5, 6, 7, 8, 9]]
            df_subset.columns = ['C', 'E', 'F', 'G', 'H', 'I', 'J']
        else:
            df_subset = df[columns_to_check]
        
        # 检查E到I列的空值
        print("\n开始处理所有行数据...")
        generated_count = 0
        skipped_count = 0
        
        for index, row in df_subset.iterrows():
            word = row['C']  # 英文单词
            chinese = row['J']  # 中文
            
            # 跳过空的单词或中文
            if pd.isna(word) or pd.isna(chinese) or str(word).strip() == '' or str(chinese).strip() == '':
                continue
                
            print(f"\n第{index+1}行 - 单词: {word}, 中文: {chinese}")
            
            # 检查各列是否为空
            e_empty = pd.isna(row['E']) or str(row['E']).strip() == ''
            f_empty = pd.isna(row['F']) or str(row['F']).strip() == ''
            g_empty = pd.isna(row['G']) or str(row['G']).strip() == ''
            h_empty = pd.isna(row['H']) or str(row['H']).strip() == ''
            i_empty = pd.isna(row['I']) or str(row['I']).strip() == ''
            
            print(f"  E列空: {e_empty}, F列空: {f_empty}, G列空: {g_empty}, H列空: {h_empty}, I列空: {i_empty}")
            
            # 生成需要的音频文件
            gen_count, skip_count = generate_audio_files(word, chinese, e_empty, f_empty, g_empty, h_empty, i_empty)
            generated_count += gen_count
            skipped_count += skip_count
        
        print(f"\n处理完成！共生成 {generated_count} 个新文件，跳过 {skipped_count} 个已存在文件。")
        return df_subset
        
    except Exception as e:
        print(f"读取Excel文件出错: {e}")
        return None

def generate_audio_files(word, chinese, e_empty, f_empty, g_empty, h_empty, i_empty):
    """根据空值情况生成对应的音频文件"""
    base_url = "http://localhost:8080/api/synthesize"
    output_dir = "/Users/lizhuang/Desktop/Model/text-to-speech/output"
    generated_count = 0
    skipped_count = 0
    
    # 清理文件名中的特殊字符
    clean_word = sanitize_filename(str(word))
    clean_chinese = sanitize_filename(str(chinese))
    
    # E列：英文
    if e_empty:
        text = word
        filename = f"{clean_word}.mp3"
        gen, skip = generate_audio(base_url, text, filename, output_dir)
        generated_count += gen
        skipped_count += skip
    
    # F列：两次英文
    if f_empty:
        text = f"{word}{word}"
        filename = f"{clean_word}{clean_word}.mp3"
        gen, skip = generate_audio(base_url, text, filename, output_dir)
        generated_count += gen
        skipped_count += skip
    
    # G列：一英一中
    if g_empty:
        text = f"{word}{chinese}"
        filename = f"{clean_word}{clean_chinese}.mp3"
        gen, skip = generate_audio(base_url, text, filename, output_dir)
        generated_count += gen
        skipped_count += skip
    
    # H列：两英一中
    if h_empty:
        text = f"{word}{word}{chinese}"
        filename = f"{clean_word}{clean_word}{clean_chinese}.mp3"
        gen, skip = generate_audio(base_url, text, filename, output_dir)
        generated_count += gen
        skipped_count += skip
    
    # I列：三次英文
    if i_empty:
        text = f"{word}{word}{word}"
        filename = f"{clean_word}{clean_word}{clean_word}.mp3"
        gen, skip = generate_audio(base_url, text, filename, output_dir)
        generated_count += gen
        skipped_count += skip
    
    return generated_count, skipped_count

def generate_audio(base_url, text, filename, output_dir):
    """调用API生成音频文件"""
    try:
        # 检查文件是否已存在
        file_path = os.path.join(output_dir, filename)
        if os.path.exists(file_path):
            print(f"  跳过已存在文件: {filename}")
            return 0, 1  # 0个生成，1个跳过
        
        data = {
            "text": text,
            "speed": 2  # 正常语速
        }
        
        print(f"  生成音频: {filename} - 文本: {text}")
        
        response = requests.post(base_url, json=data, headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"    ✓ 成功生成: {result.get('audioUrl')}")
                return 1, 0  # 1个生成，0个跳过
            else:
                print(f"    ✗ 生成失败: {result.get('error')}")
                return 0, 0
        else:
            print(f"    ✗ API调用失败: {response.status_code}")
            return 0, 0
            
    except Exception as e:
        print(f"    ✗ 生成音频出错: {e}")
        return 0, 0

def sanitize_filename(text):
    """清理文件名中的特殊字符"""
    import re
    # 移除或替换不安全的字符
    filename = re.sub(r'[<>:"/\\|?*]', '', str(text))
    filename = re.sub(r'[\r\n\t]', '', filename)
    filename = re.sub(r'\s+', '', filename)  # 去掉空格
    filename = filename.strip()
    return filename

if __name__ == "__main__":
    print("开始读取Excel文件并生成音频...")
    read_excel_data()
    print("\n处理完成！")