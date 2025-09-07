#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本转语音服务器
使用Python的gTTS库实现文本到语音的转换
"""

import os
import json
import uuid
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import tempfile

try:
    from gtts import gTTS
    from gtts.lang import tts_langs
except ImportError:
    print("请先安装gTTS库: pip install gtts")
    exit(1)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 配置目录
OUTPUT_DIR = Path('output')
OUTPUT_DIR.mkdir(exist_ok=True)

# 支持的语言
SUPPORTED_LANGUAGES = {
    'zh': '中文',
    'en': '英文',
    'zh-CN': '中文（简体）',
    'zh-TW': '中文（繁体）',
    'en-US': '英文（美国）',
    'en-GB': '英文（英国）'
}

def detect_language(text):
    """
    检测文本语言类型
    对于中英文混合文本，返回'mixed'以便特殊处理
    """
    chinese_count = 0
    english_count = 0
    
    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # 中文字符范围
            chinese_count += 1
        elif char.isascii() and char.isalpha():  # 英文字符
            english_count += 1
    
    total_chars = chinese_count + english_count
    if total_chars == 0:
        return 'zh-CN'  # 默认中文
    
    # 如果同时包含中文和英文，返回mixed
    if chinese_count > 0 and english_count > 0:
        return 'mixed'
    elif chinese_count > 0:
        return 'zh-CN'  # 标准普通话
    else:
        return 'en-US'  # 标准美式英文

def split_mixed_text(text):
    """
    将中英文混合文本分割成中文和英文片段
    """
    segments = []
    current_segment = ""
    current_lang = None
    
    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # 中文字符
            if current_lang == 'en' and current_segment.strip():
                segments.append(('en-US', current_segment.strip()))
                current_segment = ""
            current_lang = 'zh'
            current_segment += char
        elif char.isascii() and char.isalpha():  # 英文字符
            if current_lang == 'zh' and current_segment.strip():
                segments.append(('zh-CN', current_segment.strip()))
                current_segment = ""
            current_lang = 'en'
            current_segment += char
        else:  # 标点符号、空格等
            current_segment += char
    
    # 添加最后一个片段
    if current_segment.strip():
        if current_lang == 'zh':
            segments.append(('zh-CN', current_segment.strip()))
        elif current_lang == 'en':
            segments.append(('en-US', current_segment.strip()))
    
    return segments

def get_voice_lang_and_tld(lang_code, voice=None):
    """
    返回标准成人播音语言代码和TLD配置
    使用专业成人主持人音色
    
    参数:
    - lang_code: 原始语言代码
    - voice: 保留参数兼容性，但不再使用
    
    返回:
    - (语言代码, TLD) 元组
    """
    # 中文统一使用普通话，使用香港TLD获得更成人化音色
    if lang_code in ['zh', 'zh-CN', 'zh-TW']:
        return 'zh-CN', 'com.hk'  # 标准普通话，成人音色
    
    # 英文统一使用美式英语，使用澳洲TLD获得更成人化音色
    elif lang_code in ['en', 'en-US', 'en-GB']:
        return 'en', 'com.au'  # 标准美式英语，成人音色
    
    # 其他语言返回原代码，使用默认TLD
    return lang_code, 'com'

def adjust_audio_speed(audio_path, speed_factor):
    """
    调整音频播放速度
    """
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_mp3(str(audio_path))
        
        # 调整播放速度
        if speed_factor != 1.0:
            # 改变播放速度但保持音调
            new_sample_rate = int(audio.frame_rate * speed_factor)
            audio_with_new_speed = audio._spawn(audio.raw_data, overrides={"frame_rate": new_sample_rate})
            audio_with_new_speed = audio_with_new_speed.set_frame_rate(audio.frame_rate)
            return audio_with_new_speed
        return audio
    except ImportError:
        logger.warning("pydub未安装，无法调整语速")
        return AudioSegment.from_mp3(str(audio_path))

def text_to_speech(text, output_path, speed=2):
    """
    将文本转换为语音并保存为MP3文件
    对于中英文混合文本，分别处理并合并
    使用标准成人播音：普通话和美式英语
    
    参数:
    - text: 要合成的文本
    - output_path: 输出文件路径
    - speed: 语速 (0=最慢, 1=慢速, 2=正常, 3=快速, 4=最快)
    """
    try:
        # 检测文本语言
        lang = detect_language(text)
        logger.info(f"检测到语言类型: {lang}")
        
        if lang == 'mixed':
            # 处理中英文混合文本
            segments = split_mixed_text(text)
            logger.info(f"分割为 {len(segments)} 个片段")
            
            # 为每个片段生成音频
            audio_files = []
            temp_dir = Path(tempfile.mkdtemp())
            
            try:
                for i, (seg_lang, seg_text) in enumerate(segments):
                    if seg_text.strip():  # 只处理非空片段
                        temp_file = temp_dir / f"segment_{i}.mp3"
                        
                        # 使用标准播音语言代码和TLD
                        final_lang, tld = get_voice_lang_and_tld(seg_lang)
                        
                        # 根据语速设置slow参数
                        slow_mode = (speed <= 1)  # 最慢和慢速时使用slow=True
                        
                        tts = gTTS(text=seg_text, lang=final_lang, tld=tld, slow=slow_mode)
                        tts.save(str(temp_file))
                        audio_files.append(temp_file)
                        logger.info(f"片段 {i+1} ({final_lang}): {seg_text[:20]}...")
                
                # 合并音频文件
                if len(audio_files) == 1:
                    # 只有一个文件，直接移动
                    audio_files[0].rename(output_path)
                else:
                    # 多个文件需要合并
                    merge_audio_files(audio_files, output_path)
                
                # 应用语速调整
                if speed != 2:
                    # 5档语速映射: 0=0.5x, 1=0.7x, 2=1.0x, 3=1.3x, 4=1.6x
                    speed_factors = [0.5, 0.7, 1.0, 1.3, 1.6]
                    speed_factor = speed_factors[speed]
                    adjusted_audio = adjust_audio_speed(output_path, speed_factor)
                    adjusted_audio.export(str(output_path), format="mp3")
                
            finally:
                # 清理临时文件
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
        else:
            # 单一语言文本
            # 确保使用正确的语言代码
            if lang == 'zh-CN':
                lang_code = 'zh-CN'  # 普通话
            elif lang == 'en-US':
                lang_code = 'en'  # gTTS的英文代码
            else:
                lang_code = lang
            
            # 使用标准播音语言代码和TLD
            final_lang, tld = get_voice_lang_and_tld(lang_code)
            
            # 根据语速设置slow参数
            slow_mode = (speed <= 1)  # 最慢和慢速时使用slow=True
            
            tts = gTTS(text=text, lang=final_lang, tld=tld, slow=slow_mode)
            tts.save(str(output_path))
            
            # 应用语速调整
            if speed != 2:
                # 5档语速映射: 0=0.5x, 1=0.7x, 2=1.0x, 3=1.3x, 4=1.6x
                speed_factors = [0.5, 0.7, 1.0, 1.3, 1.6]
                speed_factor = speed_factors[speed]
                adjusted_audio = adjust_audio_speed(output_path, speed_factor)
                adjusted_audio.export(str(output_path), format="mp3")
        
        logger.info(f"音频文件已保存: {output_path}")
        return True, None
        
    except Exception as e:
        error_msg = f"语音合成失败: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def sanitize_filename(text):
    """
    清理文本以生成安全的文件名
    保留中英文字符，移除或替换特殊字符，直接去掉空格
    """
    # 移除或替换不安全的字符
    filename = re.sub(r'[<>:"/\\|?*]', '', text)  # 移除文件系统不允许的字符
    filename = re.sub(r'[\r\n\t]', '', filename)  # 移除换行符和制表符
    filename = re.sub(r'\s+', '', filename)  # 直接去掉空格
    filename = filename.strip()  # 去除首尾空白
    
    # 限制文件名长度
    if len(filename) > 50:
        filename = filename[:50].rstrip('_')
    
    # 如果文件名为空或只包含特殊字符，使用默认名称
    if not filename or not re.search(r'[\w\u4e00-\u9fff]', filename):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"tts_{timestamp}"
    
    return filename

def merge_audio_files(audio_files, output_path):
    """
    合并多个音频文件
    由于gTTS生成的是MP3文件，这里使用简单的文件连接
    注意：这是一个简化的实现，实际项目中建议使用pydub等库
    """
    try:
        # 尝试导入pydub进行音频合并
        from pydub import AudioSegment
        
        combined = AudioSegment.empty()
        for audio_file in audio_files:
            audio = AudioSegment.from_mp3(str(audio_file))
            combined += audio
        
        combined.export(str(output_path), format="mp3")
        
    except ImportError:
        # 如果没有pydub，使用简单的文件连接（可能有问题）
        logger.warning("未安装pydub，使用简单文件连接，可能影响音质")
        with open(output_path, 'wb') as outfile:
            for audio_file in audio_files:
                with open(audio_file, 'rb') as infile:
                    outfile.write(infile.read())

@app.route('/')
def index():
    """提供前端页面"""
    return send_from_directory('.', 'index.html')

@app.route('/api/synthesize', methods=['POST'])
def synthesize():
    """
    文本转语音API接口
    支持语速参数，使用标准成人播音
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': '缺少文本参数'}), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({'error': '文本不能为空'}), 400
        
        # 获取语速参数 (0=最慢, 1=慢速, 2=正常, 3=快速, 4=最快)
        speed = data.get('speed', 2)
        if speed not in [0, 1, 2, 3, 4]:
            speed = 2  # 默认正常语速
        
        # 使用标准成人播音，不再需要音色参数
        
        # 生成基于文本内容的文件名
        base_filename = sanitize_filename(text)
        filename = f"{base_filename}.mp3"
        output_path = OUTPUT_DIR / filename
        
        # 如果文件已存在，添加序号
        counter = 1
        while output_path.exists():
            filename = f"{base_filename}_{counter}.mp3"
            output_path = OUTPUT_DIR / filename
            counter += 1
        
        logger.info(f"开始合成语音: {text[:50]}... (语速:{['最慢','慢速','正常','快速','最快'][speed]}, 标准播音)")
        
        # 执行语音合成
        success, error_msg = text_to_speech(text, output_path, speed)
        
        if success:
            # 返回音频文件URL
            audio_url = f"/output/{filename}"
            logger.info(f"语音合成成功: {audio_url}")
            
            return jsonify({
                'success': True,
                'audioUrl': audio_url,
                'filename': filename,
                'text': text
            })
        else:
            return jsonify({'error': error_msg}), 500
            
    except Exception as e:
        logger.error(f"API处理错误: {str(e)}")
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@app.route('/output/<filename>')
def serve_audio(filename):
    """
    提供音频文件服务
    """
    try:
        # 安全检查文件名
        if not filename.endswith('.mp3'):
            return jsonify({'error': '不支持的文件类型'}), 400
        
        # 检查文件是否存在
        file_path = OUTPUT_DIR / filename
        if not file_path.exists():
            return jsonify({'error': '音频文件不存在'}), 404
        
        return send_from_directory(OUTPUT_DIR, filename)
        
    except Exception as e:
        logger.error(f"文件服务错误: {str(e)}")
        return jsonify({'error': '文件服务错误'}), 500

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """
    获取支持的语言列表
    """
    return jsonify(SUPPORTED_LANGUAGES)

@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    """
    清理旧的音频文件（可选功能）
    """
    try:
        # 清理24小时前的文件
        import time
        current_time = time.time()
        cleaned_count = 0
        
        for audio_file in OUTPUT_DIR.glob('*.mp3'):
            file_age = current_time - audio_file.stat().st_mtime
            if file_age > 24 * 3600:  # 24小时
                audio_file.unlink()
                cleaned_count += 1
        
        logger.info(f"清理了 {cleaned_count} 个旧音频文件")
        return jsonify({'cleaned': cleaned_count})
        
    except Exception as e:
        logger.error(f"清理错误: {str(e)}")
        return jsonify({'error': '清理失败'}), 500

if __name__ == '__main__':
    print("🎤 文本转语音服务器启动中...")
    print(f"📁 音频输出目录: {OUTPUT_DIR.absolute()}")
    print(f"🌐 服务器地址: http://localhost:8080")
    print("📝 支持的格式: 中文、英文、中英文混合")
    print("🔄 按 Ctrl+C 停止服务器")
    
    # 启动Flask服务器
    import threading
    import webbrowser
    
    # 延迟打开浏览器
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://localhost:8080')
    
    # 启动浏览器线程
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)