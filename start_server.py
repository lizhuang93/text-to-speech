#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本转语音服务器启动脚本
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def check_port(port):
    """检查端口是否被占用"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def kill_process_on_port(port):
    """杀掉占用指定端口的进程"""
    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        if result.stdout:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    os.kill(int(pid), signal.SIGKILL)
                    print(f"已杀掉进程 {pid}")
            time.sleep(1)
    except Exception as e:
        print(f"清理端口时出错: {e}")

def main():
    """主函数"""
    port = 8080
    
    print("🎤 文本转语音服务器启动脚本")
    print("=" * 40)
    
    # 检查端口
    if not check_port(port):
        print(f"⚠️  端口 {port} 被占用，正在清理...")
        kill_process_on_port(port)
    
    # 确保输出目录存在
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    print(f"📁 输出目录: {output_dir.absolute()}")
    
    # 设置环境变量
    env = os.environ.copy()
    env['FLASK_ENV'] = 'development'
    
    # 启动服务器
    print(f"🌐 启动服务器，端口: {port}")
    print(f"🔗 访问地址: http://localhost:{port}")
    print("🔄 按 Ctrl+C 停止服务器")
    print("=" * 40)
    
    try:
        # 使用subprocess启动服务器
        process = subprocess.Popen([
            sys.executable, '-m', 'flask', 'run',
            '--host=0.0.0.0', f'--port={port}',
            '--reload'
        ], env=env, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        # 等待服务器启动
        time.sleep(3)
        
        # 检查服务器是否正常运行
        try:
            import requests
            response = requests.get(f'http://localhost:{port}/', timeout=5)
            if response.status_code == 200:
                print("✅ 服务器启动成功！")
                print("📝 可以开始使用了！")
            else:
                print(f"⚠️  服务器响应异常: {response.status_code}")
        except Exception as e:
            print(f"⚠️  服务器可能未完全启动: {e}")
        
        # 等待进程结束
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务器...")
        process.terminate()
        process.wait()
        print("✅ 服务器已停止")
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()