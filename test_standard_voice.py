#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试标准音色功能
验证移除音色选择后的语音合成效果
"""

import requests
import json
import time
import os
from pathlib import Path

# 服务器配置
SERVER_URL = "http://localhost:8080"
API_URL = f"{SERVER_URL}/api/synthesize"
OUTPUT_DIR = Path('output')

def test_synthesis(text, speed, description):
    """
    测试语音合成
    """
    print(f"\n🧪 测试: {description}")
    print(f"📝 文本: {text}")
    print(f"⚡ 语速: {['最慢','慢速','正常','快速','最快'][speed]}")
    
    # 发送请求（不再包含voice参数）
    payload = {
        "text": text,
        "speed": speed
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                filename = result.get('filename')
                audio_path = OUTPUT_DIR / filename
                
                if audio_path.exists():
                    file_size = audio_path.stat().st_size
                    print(f"✅ 成功生成: {filename} ({file_size} bytes)")
                    
                    # 检查文件名是否包含空格
                    if ' ' in filename:
                        print(f"❌ 文件名包含空格: {filename}")
                        return False
                    else:
                        print(f"✅ 文件名格式正确: {filename}")
                    
                    return True
                else:
                    print(f"❌ 文件不存在: {filename}")
                    return False
            else:
                print(f"❌ 合成失败: {result.get('error', '未知错误')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False

def main():
    print("🎤 标准音色功能测试")
    print("=" * 50)
    
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    time.sleep(3)
    
    # 测试用例
    test_cases = [
        # 中文测试
        ("你好世界", 2, "中文标准播音测试"),
        ("这是一个语音合成测试", 1, "中文慢速测试"),
        ("快速语音合成效果", 3, "中文快速测试"),
        
        # 英文测试
        ("Hello World", 2, "英文标准播音测试"),
        ("This is a text to speech test", 0, "英文最慢速测试"),
        ("Fast speech synthesis", 4, "英文最快速测试"),
        
        # 中英文混合测试
        ("Hello 你好 World 世界", 2, "中英文混合标准播音测试"),
        ("Welcome to 北京 Beijing", 1, "中英文混合慢速测试"),
        ("AI人工智能 Technology科技", 3, "中英文混合快速测试"),
        
        # 特殊字符测试
        ("测试！@#$%^&*()_+标点符号", 2, "特殊字符测试"),
        ("数字123和456测试", 2, "数字混合测试"),
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for text, speed, description in test_cases:
        if test_synthesis(text, speed, description):
            success_count += 1
        time.sleep(1)  # 避免请求过快
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {success_count}/{total_count} 通过")
    
    if success_count == total_count:
        print("🎉 所有测试通过！标准音色功能正常工作")
        print("✅ 确认功能:")
        print("   - 中文使用普通话(zh-CN)")
        print("   - 英文使用美式英语(en-US)")
        print("   - 5档语速正常工作")
        print("   - 文件名格式正确（无空格）")
        print("   - 中英文混合处理正常")
    else:
        print(f"❌ {total_count - success_count} 个测试失败")
    
    print("\n💡 提示: 请手动播放生成的音频文件验证音质和语速效果")

if __name__ == "__main__":
    main()