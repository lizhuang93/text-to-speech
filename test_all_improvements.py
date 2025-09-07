#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有改进后的功能
- 5档语速支持
- 音色控制
- 文件名格式（去掉空格）
"""

import requests
import json
import time
import os
from pathlib import Path

# 服务器地址
BASE_URL = "http://localhost:8080"
OUTPUT_DIR = Path('output')

def test_synthesize_with_params(text, speed, voice, description):
    """
    测试语音合成API的参数
    """
    print(f"\n🧪 测试: {description}")
    print(f"📝 文本: {text}")
    print(f"🎵 语速: {['最慢', '慢速', '正常', '快速', '最快'][speed]}")
    print(f"🎤 音色: {voice}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/synthesize",
            json={
                "text": text,
                "speed": speed,
                "voice": voice
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            filename = result.get('filename', '未知文件名')
            print(f"✅ 成功: {filename}")
            
            # 检查文件是否存在
            file_path = OUTPUT_DIR / filename
            if file_path.exists():
                file_size = file_path.stat().st_size
                print(f"📁 文件大小: {file_size} bytes")
                
                # 检查文件名是否包含空格
                if ' ' in filename:
                    print(f"⚠️  文件名包含空格: {filename}")
                else:
                    print(f"✅ 文件名格式正确（无空格）: {filename}")
            else:
                print(f"❌ 文件不存在: {file_path}")
                return False
            
            return True
        else:
            error_data = response.json()
            print(f"❌ 失败: {error_data.get('error', '未知错误')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def main():
    print("🚀 开始测试所有改进后的功能")
    print("=" * 50)
    
    # 测试用例
    test_cases = [
        # 测试5档语速
        ("这是最慢语速测试。", 0, "auto", "中文最慢语速"),
        ("这是慢速语速测试。", 1, "auto", "中文慢速语速"),
        ("这是正常语速测试。", 2, "auto", "中文正常语速"),
        ("这是快速语速测试。", 3, "auto", "中文快速语速"),
        ("这是最快语速测试。", 4, "auto", "中文最快语速"),
        
        # 测试英文5档语速
        ("This is slowest speed test.", 0, "auto", "英文最慢语速"),
        ("This is fastest speed test.", 4, "auto", "英文最快语速"),
        
        # 测试音色控制
        ("你好，这是女声测试。", 2, "female", "中文女声测试"),
        ("你好，这是男声测试。", 2, "male", "中文男声测试"),
        ("Hello, this is female voice test.", 2, "female", "英文女声测试"),
        ("Hello, this is male voice test.", 2, "male", "英文男声测试"),
        
        # 测试文件名格式（包含空格的文本）
        ("hello 你好 world 世界", 2, "auto", "含空格文本测试"),
        ("Programming 编程 is fun 很有趣!", 1, "female", "混合文本含空格"),
        ("Test file name with spaces", 3, "male", "英文含空格文件名"),
        
        # 综合测试
        ("Hello你好, mixed text混合文本 test!", 0, "female", "混合文本最慢女声"),
        ("快速测试 fast test 最快语速!", 4, "male", "混合文本最快男声"),
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for text, speed, voice, description in test_cases:
        if test_synthesize_with_params(text, speed, voice, description):
            success_count += 1
        time.sleep(1)  # 避免请求过快
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {success_count}/{total_count} 成功")
    
    if success_count == total_count:
        print("🎉 所有测试通过！改进功能工作正常。")
        print("\n✅ 功能验证:")
        print("  - 5档语速支持: ✅")
        print("  - 音色控制: ✅")
        print("  - 文件名格式: ✅")
    else:
        print(f"⚠️  有 {total_count - success_count} 个测试失败，请检查日志。")
    
    print("\n💡 提示: 请手动播放生成的音频文件验证语速和音色效果。")

if __name__ == "__main__":
    main()