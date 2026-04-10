# ⚡ J.A.R.V.I.S — Just A Rather Very Intelligent System

> A personal AI assistant inspired by Iron Man's J.A.R.V.I.S., built entirely from scratch on macOS.  
> Powered by **Groq AI**, **OpenAI Whisper**, and **Python**.

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![Groq](https://img.shields.io/badge/AI-Groq%20LLaMA%203.3-orange?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey?style=flat-square&logo=apple)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 🎯 Features

- 🎙️ **"Hey Jarvis" Wake Word** — always listening, activates on your voice
- 🧠 **AI Conversations** — powered by Groq's LLaMA 3.3 70B (free tier)
- 🔊 **Voice Responses** — speaks back using macOS text-to-speech
- 🖥️ **Iron Man GUI** — animated arc reactor, dark theme, real-time clock
- 💻 **Mac System Control:**
  - Open apps (Spotify, Chrome, Safari, YouTube)
  - Control volume (up, down, mute)
  - Take screenshots
  - Search Google
  - Tell time and date

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3 | Core programming language |
| Groq API | Free AI brain (LLaMA 3.3 70B) |
| OpenAI Whisper | Local speech-to-text |
| SpeechRecognition | Wake word detection |
| Tkinter | GUI with animations |
| macOS `say` | Text-to-speech voice output |
| sounddevice + scipy | Audio recording |

---

## 🚀 Setup & Installation

### Prerequisites
- macOS
- Python 3.9+
- Homebrew

### Step 1 — Install system dependencies
```bash
brew install python ffmpeg
```

### Step 2 — Install Python packages
```bash
pip3 install groq openai-whisper sounddevice scipy SpeechRecognition pyaudio --break-system-packages
```

### Step 3 — Get your free Groq API key
Sign up at [console.groq.com](https://console.groq.com) → Create API Key (free)

### Step 4 — Set your API key permanently
```bash
echo 'export GROQ_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### Step 5 — Run Jarvis
```bash
# GUI version (recommended)
python3 jarvis_gui.py

# Terminal version
python3 jarvis.py
```

---

## 🎮 How to Use

| Command | Action |
|---------|--------|
| `Hey Jarvis` | Wake up Jarvis with your voice |
| `What time is it?` | Tells you the current time |
| `What's the date?` | Tells you today's date |
| `Open Spotify` | Opens Spotify on your Mac |
| `Open YouTube` | Opens YouTube in browser |
| `Search for [topic]` | Searches Google |
| `Volume up / down` | Controls Mac volume |
| `Take a screenshot` | Saves screenshot to Desktop |
| `reset` | Clears conversation memory |
| `switch` | Toggles voice/text mode |
| `quit` | Exits Jarvis |

---

## 📁 Project Structure

```
jarvis-ai/
├── jarvis.py          # Terminal version
├── jarvis_gui.py      # GUI version with animations
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

---

## 🧠 How It Works

```
You say "Hey Jarvis"
        ↓
SpeechRecognition detects wake word
        ↓
Whisper transcribes your command (runs locally)
        ↓
Groq API sends it to LLaMA 3.3 70B
        ↓
Jarvis speaks the response via macOS 'say'
```

---

## 👨‍💻 About

Built by **Nikith** as part of learning DevOps engineering.  
This project covers: Python, APIs, environment variables, audio processing, GUI development, Git & GitHub.

---

## 📄 License

MIT License — free to use, modify and share.

