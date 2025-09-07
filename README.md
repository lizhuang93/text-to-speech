# 🎤 文本转语音项目

一个简单易用的文本转语音Web应用，支持中文、英文和中英文混合文本的语音合成。

## ✨ 功能特点

- 🌐 支持中文、英文、中英文混合文本
- 🎵 生成高质量的MP3音频文件
- 🖥️ 简洁美观的Web界面
- 📱 响应式设计，支持移动端
- ⚡ 快速合成，实时播放
- 📁 自动保存音频文件到output目录

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
python server.py
```

### 3. 访问应用

打开浏览器访问：http://localhost:5000

## 📖 使用方法

1. 在文本框中输入要合成的文本（支持中文、英文或中英文混合）
2. 点击"合成语音"按钮
3. 等待合成完成后，点击音频播放器试听
4. 生成的MP3文件会自动保存到`output/`目录

## 🛠️ 技术栈

- **前端**: HTML5 + CSS3 + JavaScript
- **后端**: Python + Flask
- **语音合成**: Google Text-to-Speech (gTTS)
- **音频格式**: MP3

## 📁 项目结构

```
text-to-speech/
├── index.html          # 前端页面
├── server.py           # Flask后端服务器
├── requirements.txt    # Python依赖
├── output/            # 音频文件输出目录
└── README.md          # 项目说明
```

## 🔧 API接口

### 语音合成接口
- **URL**: `/api/synthesize`
- **方法**: `POST`
- **参数**: `{"text": "要合成的文本"}`
- **返回**: `{"audioUrl": "/output/filename.mp3"}`

### 获取语言列表
- **URL**: `/api/languages`
- **方法**: `GET`
- **返回**: 支持的语言列表

## ⚠️ 注意事项

- 需要网络连接（gTTS使用Google的语音合成服务）
- 生成的音频文件会保存在本地output目录
- 建议定期清理旧的音频文件以节省磁盘空间

## 🔍 故障排除

### 常见问题

1. **无法安装gTTS**
   ```bash
   pip install --upgrade pip
   pip install gtts
   ```

2. **端口被占用**
   修改`server.py`中的端口号，或关闭占用5000端口的程序

3. **无法播放音频**
   检查浏览器是否支持MP3格式，或尝试刷新页面

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！