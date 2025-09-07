#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文本转语音API
"""

import requests
import json
import time

def test_synthesize(text, base_url="http://localhost:8080"):
    """测试语音合成API"""
    print(f"正在测试: {text}")
    
    try:
        # 发送合成请求
        response = requests.post(
            f"{base_url}/api/synthesize",
            json={"text": text},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功！音频文件: {data['audioUrl']}")
            return data['audioUrl']
        else:
            print(f"❌ 失败: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def main():
    """主测试函数"""
    print("🧪 开始测试文本转语音API...")
    print("=" * 50)
    
    # 测试用例
    test_cases = [
        "你好，世界！",
        "Hello, World!",
        "hello你好",
        "这是一个中英文mixed的测试text。",
        "Good morning, 早上好！",
        "Python编程很有趣，Programming is fun!"
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}/{total_count}. ", end="")
        audio_url = test_synthesize(text)
        if audio_url:
            success_count += 1
        time.sleep(1)  # 避免请求过快
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {success_count}/{total_count} 成功")
    
    if success_count == total_count:
        print("🎉 所有测试通过！服务器运行正常。")
    else:
        print("⚠️  部分测试失败，请检查服务器日志。")

if __name__ == "__main__":
    main()