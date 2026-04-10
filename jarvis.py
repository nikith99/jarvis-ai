#!/usr/bin/env python3
"""
JARVIS v2 - Real Jarvis Experience
Built for Nikith
"""

import os
import sys
import subprocess
import tempfile
import datetime
import webbrowser

try:
    from groq import Groq
except:
    print("Run: pip3 install groq")
    sys.exit(1)

try:
    import whisper
    WHISPER_AVAILABLE = True
except:
    WHISPER_AVAILABLE = False

try:
    import sounddevice as sd
    import numpy as np
    import scipy.io.wavfile as wavfile
    AUDIO_AVAILABLE = True
except:
    AUDIO_AVAILABLE = False

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
JARVIS_NAME = "Jarvis"
VOICE = "Daniel"
SAMPLE_RATE = 16000
RECORD_SECONDS = 5
WHISPER_MODEL = "base"
GROQ_MODEL = "llama-3.3-70b-versatile"

def speak(text):
    print(f"\n🤖 {JARVIS_NAME}: {text}\n")
    subprocess.run(["say", "-v", VOICE, text])

def record_audio(duration=RECORD_SECONDS):
    if not AUDIO_AVAILABLE:
        return None
    print(f"🎤 Listening for {duration} seconds... (speak now!)")
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
    sd.wait()
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wavfile.write(tmp.name, SAMPLE_RATE, audio)
    return tmp.name

def transcribe(audio_path):
    if not WHISPER_AVAILABLE:
        return ""
    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(audio_path)
    text = result["text"].strip()
    print(f"👤 You said: \"{text}\"")
    return text

def handle_system_command(text):
    t = text.lower()

    # Time & Date
    if "date" in t or "day" in t:
        now = datetime.datetime.now()
        reply = f"Today is {now.strftime('%A, %B %d, %Y')}"
        speak(reply)
        return True

    if "time" in t:
        now = datetime.datetime.now()
        reply = f"The time is {now.strftime('%I:%M %p')}"
        speak(reply)
        return True

    # Open Apps
    apps = {"spotify": "Spotify", "chrome": "Google Chrome", "safari": "Safari",
            "notes": "Notes", "calendar": "Calendar", "terminal": "Terminal",
            "mail": "Mail", "slack": "Slack", "vscode": "Visual Studio Code",
            "youtube": None, "google": None}

    if "open" in t:
        for app, mac_name in apps.items():
            if app in t:
                if app == "youtube":
                    webbrowser.open("https://youtube.com")
                    speak("Opening YouTube for you, sir.")
                elif app == "google":
                    webbrowser.open("https://google.com")
                    speak("Opening Google for you, sir.")
                else:
                    subprocess.run(["open", "-a", mac_name])
                    speak(f"Opening {mac_name} for you, sir.")
                return True

    # Search Google
    if "search" in t or "google" in t:
        query = t.replace("search", "").replace("google", "").replace("for", "").strip()
        if query:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            speak(f"Searching Google for {query}, sir.")
            return True

    # Volume Control
    if "volume up" in t:
        subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"])
        speak("Volume increased, sir.")
        return True

    if "volume down" in t:
        subprocess.run(["osarscript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"])
        speak("Volume decreased, sir.")
        return True

    if "mute" in t:
        subprocess.run(["osascript", "-e", "set volume output muted true"])
        speak("Muted, sir.")
        return True

    if "unmute" in t:
        subprocess.run(["osarscript", "-e", "set volume output muted false"])
        speak("Unmuted, sir.")
        return True

    # Screenshot
    if "screenshot" in t:
        subprocess.run(["screencapture", "-x", f"{os.path.expanduser('~')}/Desktop/screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"])
        speak("Screenshot taken and saved to your desktop, sir.")
        return True

    return False

class JarvisAI:
    def __init__(self, api_key):
        if not api_key:
            print("\n❌ GROQ_API_KEY not set!")
            sys.exit(1)
        self.client = Groq(api_key=api_key)
        self.history = []
        self.system = (
            f"You are {JARVIS_NAME}, a highly intelligent personal AI assistant "
            "inspired by Iron Man's J.A.R.V.I.S. You speak with confidence and wit. "
            "Always address the user as 'sir'. Keep answers concise."
        )

    def chat(self, user_input):
        self.history.append({"role": "user", "content": user_input})
        response = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "system", "content": self.system}] + self.history,
            max_tokens=512
        )
        reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def reset(self):
        self.history = []
        print("🔄 Memory cleared.")

def main():
    print("=" * 55)
    print(f"  jZ  {JARVIS_NAME} v2 — Your Personal AI Assistant  ij")
    print("=" * 55)
    print("""
Commands you can use:
  open spotify | open chrome | open safari | open youtube
  what time is it | what's the date
  search [topic] | google [topic]
  volume up | volume down | mute | unmute
  screenshot
  Xany question or conversation X
  reset | switch | quit
""")

    if not WHISPER_AVAILABLE or not AUDIO_AVAILABLE:
        print("⚠️  Voice unavailable. Running in TEXT mode.\n")
        mode = "text"
    else:
        print("[v] Voice mode\n[t] Text mode")
        choice = input("\nChoose mode (v/t): ").strip().lower()
        mode = "voice" if choice == "v" else "text"

    print(f"\nRunning in {mode.upper()} mode.\n")
    jarvis = JarvisAI(api_key=GROQ_API_KEY)
    speak(f"Good day, sir. I am {JARVIS_NAME}. All systems are online and ready to assist you.")

    while True:
        try:
            if mode == "voice":
                audio_file = record_audio()
                if not audio_file:
                    continue
                user_input = transcribe(audio_file)
                os.unlink(audio_file)
                if not user_input:
                    continue
            else:
                user_input = input("👤 You: ").strip()

            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit", "bye"]:
                speak("Goodbye, sir. Jarvis going offline.")
                break
            elif user_input.lower() == "reset":
                jarvis.reset()
                speak("Memory wiped, sir. Starting fresh.")
            elif user_input.lower() == "switch":
                mode = "text" if mode == "voice" else "voice"
                speak(f"Switched to {mode} mode, sir.")
            elif handle_system_command(user_input):
                pass
            else:
                reply = jarvis.chat(user_input)
                speak(reply)

        except KeyboardInterrupt:
            print("\nGoodbye!)")
            break
        except Exception as e:
            print(f"\n⚠️  Error: {e}")

if __name__ == "__main__":
    main()
