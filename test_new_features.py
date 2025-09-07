#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新增的语速和音色功能
"""

import requests
import json
import time

# 服务器地址
BASE_URL = "http://localhost:8080"

def test_synthesize_with_params(text, speed, voice, description):
    """
    测试语音合成API的新参数
    """
    print(f"\n🧪 测试: {description}")
    print(f"📝 文本: {text}")
    print(f"🎵 语速: {['慢速', '正常', '快速'][speed]}")
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
            print(f"✅ 成功: {result.get('filename', '未知文件名')}")
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
    print("🚀 开始测试新的语速和音色功能")
    print("=" * 50)
    
    # 测试用例
    test_cases = [
        # 测试不同语速
        ("Hello, this is a speed test.", 0, "auto", "英文慢速测试"),
        ("Hello, this is a speed test.", 1, "auto", "英文正常语速测试"),
        ("Hello, this is a speed test.", 2, "auto", "英文快速测试"),
        
        # 测试不同音色
        ("你好，这是音色测试。", 1, "female", "中文女声测试"),
        ("你好，这是音色测试。", 1, "male", "中文男声测试"),
        ("Hello, this is a voice test.", 1, "female", "英文女声测试"),
        ("Hello, this is a voice test.", 1, "male", "英文男声测试"),
        
        # 测试混合文本
        ("Hello你好, this is a mixed test混合测试.", 0, "female", "混合文本慢速女声"),
        ("Programming编程 is fun很有趣!", 2, "male", "混合文本快速男声"),
        
        # 测试智能音色
        ("智能音色测试，应该自动选择合适的声音。", 1, "auto", "中文智能音色"),
        ("Auto voice test, should choose appropriate voice.", 1, "auto", "英文智能音色"),
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
        print("🎉 所有测试通过！新功能工作正常。")
    else:
        print(f"⚠️  有 {total_count - success_count} 个测试失败，请检查日志。")

if __name__ == "__main__":
    main()