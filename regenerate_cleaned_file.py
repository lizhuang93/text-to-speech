#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import re

def has_need_translation_format(text):
    """检查是否包含[需要翻译：xxx]格式"""
    if not text or pd.isna(text):
        return False
    # 匹配[需要翻译: xxx]或[需要翻译：xxx]格式（支持中英文冒号）
    pattern = r'\[需要翻译[：:]\s*([^\]]+)\]'
    return bool(re.search(pattern, str(text)))

def main():
    # 检查可用的源文件
    possible_sources = [
        '/Users/lizhuang/Desktop/Model/text-to-speech/音频缺少数据_simple_translated.xlsx',
        '/Users/lizhuang/Desktop/Model/text-to-speech/音频缺少数据_final_translated.xlsx',
        '/Users/lizhuang/Desktop/Model/text-to-speech/音频缺少数据.xlsx'
    ]
    
    input_file = None
    for source in possible_sources:
        try:
            df_test = pd.read_excel(source)
            input_file = source
            print(f"找到源文件: {source}")
            break
        except:
            continue
    
    if not input_file:
        print("错误: 未找到任何可用的源文件")
        print("请确保以下文件之一存在:")
        for source in possible_sources:
            print(f"  - {source}")
        return
    
    output_file = '/Users/lizhuang/Desktop/Model/text-to-speech/音频缺少数据_cleaned.xlsx'
    
    print(f"正在从 {input_file} 重新生成 cleaned 文件...")
    
    try:
        df = pd.read_excel(input_file)
        print(f"读取成功，共 {len(df)} 行数据")
    except Exception as e:
        print(f"读取文件失败: {e}")
        return
    
    print(f"\n文件列信息:")
    print(f"列名: {list(df.columns)}")
    
    # 查找J列或类似的翻译结果列
    translation_column = None
    for col in df.columns:
        if 'J' == col or '翻译' in str(col) or 'translation' in str(col).lower():
            translation_column = col
            break
    
    if not translation_column:
        print("警告: 未找到翻译列，将直接复制文件")
        df.to_excel(output_file, index=False)
        print(f"文件已保存到: {output_file}")
        return
    
    print(f"使用翻译列: {translation_column}")
    
    # 统计需要删除的行
    rows_to_remove = []
    for index, row in df.iterrows():
        translation_value = row[translation_column]
        if has_need_translation_format(translation_value):
            rows_to_remove.append(index)
    
    print(f"找到 {len(rows_to_remove)} 行包含[需要翻译：xxx]格式，将被删除")
    
    if len(rows_to_remove) > 0:
        # 显示前几个要删除的行
        print("\n前10个要删除的行:")
        for i, row_index in enumerate(rows_to_remove[:10]):
            translation_content = df.iloc[row_index][translation_column]
            print(f"{i+1}. 行{row_index+1}: {translation_content}")
        
        if len(rows_to_remove) > 10:
            print(f"... 还有 {len(rows_to_remove) - 10} 行")
        
        # 删除包含[需要翻译：xxx]格式的行
        df_cleaned = df.drop(rows_to_remove).reset_index(drop=True)
    else:
        print("没有找到需要删除的行，直接使用原数据")
        df_cleaned = df.copy()
    
    print(f"\n删除后剩余 {len(df_cleaned)} 行数据")
    
    # 保存清理后的文件
    print(f"正在保存清理后的文件到 {output_file}...")
    try:
        df_cleaned.to_excel(output_file, index=False)
        print("保存成功!")
    except Exception as e:
        print(f"保存失败: {e}")
        return
    
    # 输出统计信息
    print(f"\n=== 重新生成完成 ===")
    print(f"源文件: {input_file}")
    print(f"输出文件: {output_file}")
    print(f"原始行数: {len(df)}")
    print(f"删除行数: {len(rows_to_remove)}")
    print(f"剩余行数: {len(df_cleaned)}")
    if len(df) > 0:
        print(f"删除比例: {(len(rows_to_remove)/len(df)*100):.1f}%")
    
    # 验证清理结果
    remaining_untranslated = 0
    if translation_column:
        for index, row in df_cleaned.iterrows():
            if has_need_translation_format(row[translation_column]):
                remaining_untranslated += 1
    
    if remaining_untranslated == 0:
        print("\n✅ 验证通过：清理后的文件中没有[需要翻译：xxx]格式的条目")
    else:
        print(f"\n⚠️  警告：清理后仍有 {remaining_untranslated} 个[需要翻译：xxx]格式的条目")
    
    # 生成清理报告
    report_file = '/Users/lizhuang/Desktop/Model/text-to-speech/regeneration_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("音频缺少数据_cleaned.xlsx 重新生成报告\n")
        f.write("=" * 50 + "\n")
        f.write(f"源文件: {input_file}\n")
        f.write(f"输出文件: {output_file}\n")
        f.write(f"原始行数: {len(df)}\n")
        f.write(f"删除行数: {len(rows_to_remove)}\n")
        f.write(f"剩余行数: {len(df_cleaned)}\n")
        if len(df) > 0:
            f.write(f"删除比例: {(len(rows_to_remove)/len(df)*100):.1f}%\n")
        f.write(f"使用的翻译列: {translation_column}\n")
        f.write("\n删除的行列表:\n")
        for row_index in rows_to_remove:
            translation_content = df.iloc[row_index][translation_column]
            f.write(f"行{row_index+1}: {translation_content}\n")
    
    print(f"重新生成报告已保存到: {report_file}")

if __name__ == "__main__":
    main()