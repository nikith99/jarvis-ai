#!/usr/bin/env python3
"""
JARVIS GUI - Iron Man Style AI Assistant
With "Hey Jarvis" Wake Word Detection
Built for Nikith
"""

import os
import sys
import subprocess
import tempfile
import threading
import datetime
import webbrowser
import math
import time
import tkinter as tk
from tkinter import scrolledtext

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

try:
    from groq import Groq
except ImportError:
    print("Run: pip3 install groq --break-system-packages")
    sys.exit(1)

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    import sounddevice as sd
    import numpy as np
    import scipy.io.wavfile as wavfile
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

# ── CONFIG ────────────────────────────────────────────────────────────────────
GROQ_API_KEY   = os.environ.get("GROQ_API_KEY", "")
JARVIS_NAME    = "Jarvis"
VOICE          = "Daniel"
SAMPLE_RATE    = 16000
RECORD_SECONDS = 5
WHISPER_MODEL  = "base"
GROQ_MODEL     = "llama-3.3-70b-versatile"

# ── COLORS (Iron Man theme) ───────────────────────────────────────────────────
BG_COLOR       = "#0a0e1a"
PANEL_COLOR    = "#0d1426"
ACCENT         = "#00d4ff"
ACCENT2        = "#ff6b00"
TEXT_COLOR     = "#c8e6f0"
DIM_TEXT       = "#4a7a8a"
GLOW_COLOR     = "#00aacc"
GREEN          = "#00ff88"
RED            = "#ff3355"
BORDER         = "#1a3a4a"

# ── SPEAK ─────────────────────────────────────────────────────────────────────
def speak(text):
    subprocess.Popen(["say", "-v", VOICE, text])

# ── RECORD AUDIO ─────────────────────────────────────────────────────────────
def record_audio(duration=RECORD_SECONDS):
    if not AUDIO_AVAILABLE:
        return None
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
    sd.wait()
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wavfile.write(tmp.name, SAMPLE_RATE, audio)
    return tmp.name

# ── TRANSCRIBE ────────────────────────────────────────────────────────────────
def transcribe(audio_path):
    if not WHISPER_AVAILABLE:
        return ""
    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(audio_path)
    return result["text"].strip()

# ── SYSTEM COMMANDS ───────────────────────────────────────────────────────────
def handle_system_command(text):
    t = text.lower()
    if "date" in t or "day" in t:
        now = datetime.datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}, sir."
    if "time" in t:
        now = datetime.datetime.now()
        return f"The time is {now.strftime('%I:%M %p')}, sir."
    apps = {"spotify": "Spotify", "chrome": "Google Chrome", "safari": "Safari",
            "notes": "Notes", "calendar": "Calendar", "mail": "Mail", "slack": "Slack"}
    if "open" in t:
        if "youtube" in t:
            webbrowser.open("https://youtube.com")
            return "Opening YouTube for you, sir."
        if "google" in t:
            webbrowser.open("https://google.com")
            return "Opening Google for you, sir."
        for app, mac_name in apps.items():
            if app in t:
                subprocess.Popen(["open", "-a", mac_name])
                return f"Opening {mac_name} for you, sir."
    if "search" in t or ("google" in t and "open" not in t):
        query = t.replace("search", "").replace("google", "").replace("for", "").strip()
        if query:
            webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            return f"Searching Google for {query}, sir."
    if "volume up" in t:
        subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"])
        return "Volume increased, sir."
    if "volume down" in t:
        subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"])
        return "Volume decreased, sir."
    if "mute" in t:
        subprocess.run(["osascript", "-e", "set volume output muted true"])
        return "Muted, sir."
    if "screenshot" in t:
        path = f"{os.path.expanduser('~')}/Desktop/screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        subprocess.run(["screencapture", "-x", path])
        return "Screenshot saved to your desktop, sir."
    return None

# ── JARVIS AI ─────────────────────────────────────────────────────────────────
class JarvisAI:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        self.history = []
        self.system = (
            f"You are {JARVIS_NAME}, a highly intelligent AI assistant inspired by "
            "Iron Man's J.A.R.V.I.S. Speak with confidence and wit. Always call the "
            "user 'sir'. Keep answers short and sharp (2-3 sentences max)."
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


# ── GUI ───────────────────────────────────────────────────────────────────────
class JarvisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("J.A.R.V.I.S")
        self.root.geometry("900x650")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.jarvis = JarvisAI(api_key=GROQ_API_KEY)
        self.mode = "text"
        self.is_listening = False
        self.is_speaking = False
        self.wake_word_active = False
        self.ring_angle = 0
        self.pulse_radius = 60
        self.pulse_growing = True
        self.particles = []
        self.boot_complete = False

        self._build_ui()
        self._animate()
        self._boot_sequence()
        if SR_AVAILABLE:
            threading.Thread(target=self._wake_word_listener, daemon=True).start()

    # ── BUILD UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=BG_COLOR, height=60)
        header.pack(fill="x", padx=20, pady=(15, 0))

        tk.Label(header, text="J.A.R.V.I.S", font=("Courier", 28, "bold"),
                 fg=ACCENT, bg=BG_COLOR).pack(side="left")
        tk.Label(header, text="Just A Rather Very Intelligent System",
                 font=("Courier", 9), fg=DIM_TEXT, bg=BG_COLOR).pack(side="left", padx=15, pady=8)

        self.status_dot = tk.Label(header, text="●", font=("Courier", 14),
                                    fg=GREEN, bg=BG_COLOR)
        self.status_dot.pack(side="right")
        self.status_label = tk.Label(header, text="ONLINE", font=("Courier", 10, "bold"),
                                      fg=GREEN, bg=BG_COLOR)
        self.status_label.pack(side="right", padx=5)

        # Clock
        self.clock_label = tk.Label(header, text="", font=("Courier", 11),
                                     fg=DIM_TEXT, bg=BG_COLOR)
        self.clock_label.pack(side="right", padx=20)

        # Divider
        tk.Frame(self.root, bg=ACCENT, height=1).pack(fill="x", padx=20)

        # Main area
        main = tk.Frame(self.root, bg=BG_COLOR)
        main.pack(fill="both", expand=True, padx=20, pady=10)

        # Left panel — arc reactor animation
        left = tk.Frame(main, bg=PANEL_COLOR, width=220,
                         highlightbackground=BORDER, highlightthickness=1)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)

        tk.Label(left, text="ARC REACTOR", font=("Courier", 8),
                 fg=DIM_TEXT, bg=PANEL_COLOR).pack(pady=(15, 5))

        self.canvas = tk.Canvas(left, width=180, height=180, bg=PANEL_COLOR,
                                 highlightthickness=0)
        self.canvas.pack(pady=10)

        # Mode & stats
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=10, pady=5)

        self.mode_label = tk.Label(left, text="MODE: TEXT", font=("Courier", 9, "bold"),
                                    fg=ACCENT, bg=PANEL_COLOR)
        self.mode_label.pack(pady=3)

        tk.Label(left, text="STATUS", font=("Courier", 8), fg=DIM_TEXT, bg=PANEL_COLOR).pack()
        self.status_text = tk.Label(left, text="READY", font=("Courier", 10, "bold"),
                                     fg=GREEN, bg=PANEL_COLOR)
        self.status_text.pack(pady=2)

        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=10, pady=8)
        tk.Label(left, text="COMMANDS", font=("Courier", 8, "bold"),
                 fg=DIM_TEXT, bg=PANEL_COLOR).pack()

        commands = ["what time is it", "open youtube", "search [topic]",
                    "volume up/down", "screenshot", "reset | switch | quit"]
        for cmd in commands:
            tk.Label(left, text=f"› {cmd}", font=("Courier", 7),
                     fg=DIM_TEXT, bg=PANEL_COLOR, wraplength=180, justify="left").pack(
                         anchor="w", padx=12, pady=1)

        # Right panel — chat
        right = tk.Frame(main, bg=BG_COLOR)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="COMMUNICATION LOG", font=("Courier", 9),
                 fg=DIM_TEXT, bg=BG_COLOR).pack(anchor="w")

        self.chat_box = scrolledtext.ScrolledText(
            right, bg=PANEL_COLOR, fg=TEXT_COLOR,
            font=("Courier", 11), wrap=tk.WORD,
            insertbackground=ACCENT, relief="flat",
            highlightbackground=BORDER, highlightthickness=1
        )
        self.chat_box.pack(fill="both", expand=True, pady=(5, 10))
        self.chat_box.config(state="disabled")
        self.chat_box.tag_config("jarvis", foreground=ACCENT)
        self.chat_box.tag_config("user", foreground=ACCENT2)
        self.chat_box.tag_config("system", foreground=DIM_TEXT)
        self.chat_box.tag_config("error", foreground=RED)

        # Input area
        input_frame = tk.Frame(right, bg=BG_COLOR)
        input_frame.pack(fill="x")

        self.input_field = tk.Entry(
            input_frame, bg=PANEL_COLOR, fg=TEXT_COLOR,
            font=("Courier", 12), insertbackground=ACCENT,
            relief="flat", highlightbackground=ACCENT,
            highlightthickness=1
        )
        self.input_field.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        self.input_field.bind("<Return>", self._on_send)

        self.send_btn = tk.Button(
            input_frame, text="SEND", font=("Courier", 10, "bold"),
            bg=ACCENT, fg=BG_COLOR, relief="flat",
            activebackground=GLOW_COLOR, activeforeground=BG_COLOR,
            cursor="hand2", command=self._on_send, padx=15
        )
        self.send_btn.pack(side="left")

        if AUDIO_AVAILABLE and WHISPER_AVAILABLE:
            self.mic_btn = tk.Button(
                input_frame, text="🎤", font=("Arial", 14),
                bg=PANEL_COLOR, fg=ACCENT2, relief="flat",
                activebackground=RED, cursor="hand2",
                command=self._on_mic, padx=8
            )
            self.mic_btn.pack(side="left", padx=(5, 0))

        # Bottom bar
        tk.Frame(self.root, bg=ACCENT, height=1).pack(fill="x", padx=20)
        bottom = tk.Frame(self.root, bg=BG_COLOR)
        bottom.pack(fill="x", padx=20, pady=5)

        self.bottom_status = tk.Label(bottom, text="ALL SYSTEMS NOMINAL",
                                       font=("Courier", 8), fg=DIM_TEXT, bg=BG_COLOR)
        self.bottom_status.pack(side="left")

        tk.Label(bottom, text="NIKITH // AUTHORIZED USER",
                 font=("Courier", 8), fg=DIM_TEXT, bg=BG_COLOR).pack(side="right")

    # ── BOOT SEQUENCE ─────────────────────────────────────────────────────────
    def _boot_sequence(self):
        messages = [
            ("system", "[ INITIALIZING J.A.R.V.I.S... ]"),
            ("system", "[ LOADING AI CORE... OK ]"),
            ("system", "[ VOICE SYSTEMS... OK ]"),
            ("system", "[ CONNECTING TO GROQ API... OK ]"),
            ("system", "[ ALL SYSTEMS ONLINE ]"),
            ("system", "─" * 45),
        ]

        def show_next(i):
            if i < len(messages):
                tag, msg = messages[i]
                self._log(msg, tag)
                self.root.after(400, lambda: show_next(i + 1))
            else:
                self.boot_complete = True
                self._log(f"{JARVIS_NAME}: Good day, sir. All systems are online and ready to assist you.", "jarvis")
                threading.Thread(target=lambda: speak("Good day, sir. All systems are online and ready to assist you."), daemon=True).start()

        self.root.after(300, lambda: show_next(0))

    # ── LOGGING ───────────────────────────────────────────────────────────────
    def _log(self, text, tag="system"):
        self.chat_box.config(state="normal")
        self.chat_box.insert("end", text + "\n", tag)
        self.chat_box.see("end")
        self.chat_box.config(state="disabled")

    # ── SEND MESSAGE ──────────────────────────────────────────────────────────
    def _on_send(self, event=None):
        if not self.boot_complete:
            return
        text = self.input_field.get().strip()
        if not text:
            return
        self.input_field.delete(0, "end")
        self._process_input(text)

    def _process_input(self, text):
        self._log(f"You: {text}", "user")
        self._set_status("THINKING...", ACCENT)

        def run():
            try:
                # Check system commands first
                sys_reply = handle_system_command(text)
                if text.lower() in ["quit", "exit", "bye"]:
                    self._log(f"{JARVIS_NAME}: Goodbye, sir. Jarvis going offline.", "jarvis")
                    speak("Goodbye, sir. Jarvis going offline.")
                    self.root.after(2000, self.root.destroy)
                    return
                if text.lower() == "reset":
                    self.jarvis.reset()
                    reply = "Memory wiped, sir. Starting fresh."
                elif text.lower() == "switch":
                    self.mode = "voice" if self.mode == "text" else "text"
                    reply = f"Switched to {self.mode} mode, sir."
                    self.mode_label.config(text=f"MODE: {self.mode.upper()}")
                elif sys_reply:
                    reply = sys_reply
                else:
                    reply = self.jarvis.chat(text)

                self.root.after(0, lambda: self._log(f"{JARVIS_NAME}: {reply}", "jarvis"))
                self.root.after(0, lambda: self._set_status("SPEAKING", ACCENT2))
                speak(reply)
                self.root.after(0, lambda: self._set_status("READY", GREEN))
            except Exception as e:
                self.root.after(0, lambda: self._log(f"Error: {e}", "error"))
                self.root.after(0, lambda: self._set_status("ERROR", RED))

        threading.Thread(target=run, daemon=True).start()

    # ── MIC BUTTON ────────────────────────────────────────────────────────────
    def _on_mic(self):
        if self.is_listening:
            return
        self.is_listening = True
        self._set_status("LISTENING...", RED)
        self._log("🎤 Listening...", "system")

        def run():
            try:
                audio_file = record_audio()
                if audio_file:
                    self.root.after(0, lambda: self._set_status("TRANSCRIBING...", ACCENT))
                    text = transcribe(audio_file)
                    os.unlink(audio_file)
                    if text:
                        self.root.after(0, lambda: self._process_input(text))
                    else:
                        self.root.after(0, lambda: self._log("Could not hear anything.", "system"))
                        self.root.after(0, lambda: self._set_status("READY", GREEN))
            except Exception as e:
                self.root.after(0, lambda: self._log(f"Mic error: {e}", "error"))
            finally:
                self.is_listening = False

        threading.Thread(target=run, daemon=True).start()

    # ── WAKE WORD LISTENER ────────────────────────────────────────────────────
    def _wake_word_listener(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        recognizer.energy_threshold = 3000
        recognizer.dynamic_energy_threshold = True

        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)

        self.root.after(0, lambda: self._log("[ WAKE WORD DETECTION ACTIVE — say 'Hey Jarvis' ]", "system"))

        while True:
            try:
                with mic as source:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
                text = recognizer.recognize_google(audio).lower()

                if "jarvis" in text or "hey jarvis" in text:
                    self.root.after(0, lambda: self._log("🔊 Wake word detected!", "system"))
                    self.root.after(0, lambda: self._set_status("LISTENING...", RED))
                    speak("Yes sir, how can I help?")

                    # Now listen for the actual command
                    with mic as source:
                        self.root.after(0, lambda: self._log("🎤 Listening for command...", "system"))
                        audio2 = recognizer.listen(source, timeout=6, phrase_time_limit=8)

                    command = recognizer.recognize_google(audio2)
                    self.root.after(0, lambda c=command: self._process_input(c))

            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except Exception as e:
                time.sleep(1)
                continue

    # ── STATUS ────────────────────────────────────────────────────────────────
    def _set_status(self, text, color):
        self.status_text.config(text=text, fg=color)
        self.bottom_status.config(text=text)

    # ── ANIMATION LOOP ────────────────────────────────────────────────────────
    def _animate(self):
        self._draw_arc_reactor()
        self._update_clock()
        self.root.after(30, self._animate)

    def _draw_arc_reactor(self):
        self.canvas.delete("all")
        cx, cy = 90, 90

        # Outer rotating ring
        self.ring_angle = (self.ring_angle + 2) % 360
        for i in range(12):
            angle = math.radians(self.ring_angle + i * 30)
            x = cx + 75 * math.cos(angle)
            y = cy + 75 * math.sin(angle)
            alpha = int(255 * (i / 12))
            color = f"#{0:02x}{int(alpha * 0.83):02x}{int(alpha):02x}"
            try:
                self.canvas.create_oval(x-3, y-3, x+3, y+3, fill=ACCENT, outline="")
            except:
                pass

        # Outer ring
        self.canvas.create_oval(cx-75, cy-75, cx+75, cy+75,
                                  outline=ACCENT, width=1)

        # Middle ring (counter rotating)
        angle2 = math.radians(-self.ring_angle * 1.5)
        for i in range(6):
            a = math.radians(-self.ring_angle * 1.5 + i * 60)
            x = cx + 55 * math.cos(a)
            y = cy + 55 * math.sin(a)
            self.canvas.create_oval(x-2, y-2, x+2, y+2, fill=ACCENT2, outline="")

        self.canvas.create_oval(cx-55, cy-55, cx+55, cy+55,
                                  outline=BORDER, width=1)

        # Pulse effect
        if self.pulse_growing:
            self.pulse_radius += 0.5
            if self.pulse_radius >= 35:
                self.pulse_growing = False
        else:
            self.pulse_radius -= 0.5
            if self.pulse_radius <= 25:
                self.pulse_growing = True

        # Inner glow circles
        for r, alpha in [(40, "#0a2a3a"), (35, "#0d3a4a"), (30, "#0f4a5a")]:
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=alpha, outline=GLOW_COLOR, width=1)

        # Core
        self.canvas.create_oval(
            cx - self.pulse_radius, cy - self.pulse_radius,
            cx + self.pulse_radius, cy + self.pulse_radius,
            fill=ACCENT, outline=ACCENT, stipple="gray50"
        )
        self.canvas.create_oval(cx-18, cy-18, cx+18, cy+18, fill=ACCENT, outline="white", width=1)
        self.canvas.create_oval(cx-8, cy-8, cx+8, cy+8, fill="white", outline="")

        # Hex lines
        for angle_deg in range(0, 360, 60):
            angle_rad = math.radians(angle_deg)
            x1 = cx + 20 * math.cos(angle_rad)
            y1 = cy + 20 * math.sin(angle_rad)
            x2 = cx + 40 * math.cos(angle_rad)
            y2 = cy + 40 * math.sin(angle_rad)
            self.canvas.create_line(x1, y1, x2, y2, fill=ACCENT, width=1)

    def _update_clock(self):
        now = datetime.datetime.now()
        self.clock_label.config(text=now.strftime("%H:%M:%S"))


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not set!")
        print("   Run: export GROQ_API_KEY='your-key-here'")
        sys.exit(1)

    root = tk.Tk()
    app = JarvisGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
