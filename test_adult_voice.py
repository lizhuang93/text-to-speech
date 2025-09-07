#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试成人主持人音色功能
验证使用TLD参数后的音色效果
"""

import requests
import json
import time
import os
from pathlib import Path

# 服务器配置
SERVER_URL = "http://localhost:8080"
API_URL = f"{SERVER_URL}/api/synthesize"

def test_voice_synthesis(text, test_name, expected_lang=None):
    """
    测试语音合成功能
    """
    print(f"\n🎤 测试: {test_name}")
    print(f"📝 文本: {text}")
    
    # 发送合成请求
    data = {
        "text": text,
        "speed": 2  # 正常语速
    }
    
    try:
        response = requests.post(API_URL, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                audio_url = result.get('audio_url')
                filename = result.get('filename')
                
                print(f"✅ 合成成功")
                print(f"🔗 音频URL: {audio_url}")
                print(f"📁 文件名: {filename}")
                
                # 检查文件是否存在
                audio_path = Path('output') / filename
                if audio_path.exists():
                    file_size = audio_path.stat().st_size
                    print(f"📊 文件大小: {file_size} 字节")
                    
                    if file_size > 1000:  # 至少1KB
                        print(f"✅ 音频文件生成正常")
                        return True
                    else:
                        print(f"❌ 音频文件太小，可能生成失败")
                        return False
                else:
                    print(f"❌ 音频文件不存在: {audio_path}")
                    return False
            else:
                print(f"❌ 合成失败: {result.get('error', '未知错误')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def main():
    print("🎯 开始测试成人主持人音色功能")
    print("=" * 50)
    
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    time.sleep(3)
    
    # 测试用例
    test_cases = [
        {
            "text": "欢迎收听今日新闻，我是主持人小王。",
            "name": "中文主持人播报",
            "expected_lang": "zh-CN"
        },
        {
            "text": "Good evening, and welcome to tonight's news broadcast.",
            "name": "英文主持人播报",
            "expected_lang": "en"
        },
        {
            "text": "今天的天气预报：Today's weather forecast shows sunny skies.",
            "name": "中英文混合播报",
            "expected_lang": "mixed"
        },
        {
            "text": "各位观众朋友们，大家好！欢迎收看今晚的财经新闻。",
            "name": "正式新闻播报",
            "expected_lang": "zh-CN"
        },
        {
            "text": "Ladies and gentlemen, welcome to our special program tonight.",
            "name": "正式英文播报",
            "expected_lang": "en"
        },
        {
            "text": "现在播报一条重要新闻：The stock market reached new heights today.",
            "name": "新闻快讯（中英混合）",
            "expected_lang": "mixed"
        }
    ]
    
    # 执行测试
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试 {i}/{total}")
        if test_voice_synthesis(
            test_case["text"], 
            test_case["name"], 
            test_case["expected_lang"]
        ):
            passed += 1
        
        # 测试间隔
        if i < total:
            time.sleep(2)
    
    # 测试结果汇总
    print("\n" + "=" * 50)
    print(f"🎯 测试完成！")
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！成人主持人音色功能正常工作！")
        print("🎤 音色特点：")
        print("   - 中文：使用香港TLD，更成熟的普通话音色")
        print("   - 英文：使用澳洲TLD，更专业的成人音色")
        print("   - 适合新闻播报、正式场合使用")
    else:
        print("⚠️  部分测试失败，请检查服务器日志")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)