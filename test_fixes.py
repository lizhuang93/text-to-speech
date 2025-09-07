#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修正后的语速和音色功能
"""

import requests
import json
import time
import os
from pathlib import Path

def test_synthesize_with_fixes():
    """
    测试修正后的语速和音色功能
    """
    base_url = "http://localhost:8080"
    
    test_cases = [
        # 测试语速变化
        {"text": "这是语速测试", "speed": 0, "voice": "auto", "name": "慢速测试"},
        {"text": "这是语速测试", "speed": 1, "voice": "auto", "name": "正常速度测试"},
        {"text": "这是语速测试", "speed": 2, "voice": "auto", "name": "快速测试"},
        
        # 测试音色变化
        {"text": "Hello world", "speed": 1, "voice": "female", "name": "英文女声测试"},
        {"text": "Hello world", "speed": 1, "voice": "male", "name": "英文男声测试"},
        {"text": "你好世界", "speed": 1, "voice": "female", "name": "中文女声测试"},
        {"text": "你好世界", "speed": 1, "voice": "male", "name": "中文男声测试"},
        
        # 测试文件名（检查空格是否被替换）
        {"text": "测试 文件 名称", "speed": 1, "voice": "auto", "name": "文件名测试"},
    ]
    
    print("开始测试修正后的功能...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"文本: {test_case['text']}")
        print(f"语速: {test_case['speed']}, 音色: {test_case['voice']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/synthesize",
                json={
                    "text": test_case['text'],
                    "speed": test_case['speed'],
                    "voice": test_case['voice']
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    filename = result.get('filename')
                    print(f"✅ 成功生成: {filename}")
                    
                    # 检查文件是否存在
                    file_path = Path(f"output/{filename}")
                    if file_path.exists():
                        file_size = file_path.stat().st_size
                        print(f"   文件大小: {file_size} bytes")
                        
                        # 检查文件名是否包含空格
                        if ' ' in filename:
                            print(f"   ⚠️  警告: 文件名仍包含空格: {filename}")
                        else:
                            print(f"   ✅ 文件名正确（无空格）: {filename}")
                    else:
                        print(f"   ❌ 文件不存在: {filename}")
                else:
                    print(f"   ❌ 合成失败: {result.get('error', '未知错误')}")
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 请求异常: {str(e)}")
        
        # 等待一下再进行下一个测试
        time.sleep(1)
    
    print("\n测试完成！")
    print("\n请手动播放生成的音频文件来验证:")
    print("1. 语速是否有明显变化")
    print("2. 音色是否有差异")
    print("3. 文件名是否正确（无空格）")

if __name__ == "__main__":
    test_synthesize_with_fixes()