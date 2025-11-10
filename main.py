
"""
Desktop Voice Assistant with Tkinter UI (Full Version)
Features:
- Classic Tkinter UI (voice + text input)
- Play YouTube, search web, play local music
- Take screenshots, system info, jokes
- Open apps, shutdown/restart
- Chatbot (rule-based fallback)
- System controls: volume (media keys), brightness (Windows via PowerShell)
- File/folder open, reminders, save logs, always-on-top toggle

Requirements:
- Python 3.8+
- pip install pyttsx3 SpeechRecognition pywhatkit pyautogui psutil pyjokes Pillow
- On Windows: pyaudio (install via pipwin if needed)

Run: python desktop_assistant_gui_full.py
"""

import threading
import time
import os
import random
import datetime
import webbrowser as wb
from pathlib import Path
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import pyttsx3
import speech_recognition as sr
import pywhatkit
import pyautogui
import psutil
import pyjokes

# ------------------- CONFIG -------------------
USER_NAME = os.getlogin() if hasattr(os, 'getlogin') else 'user'
MUSIC_FOLDER = Path.home() / 'Music' / 'Playlists'
DEFAULT_APPS = {
    'notepad': 'notepad.exe',
    'calculator': 'calc.exe',
    'chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    'vscode': fr'C:\Users\{USER_NAME}\AppData\Local\Programs\Microsoft VS Code\Code.exe'
}

# ------------------- TTS SETUP -------------------
engine = pyttsx3.init('sapi5') if os.name == 'nt' else pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id if voices else '')
engine.setProperty('rate', 160)

# ------------------- UTILS -------------------

def speak(text: str):
    """Speak text and optionally print to console."""
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception:
        print('TTS failed')


def recognize_speech(timeout=6, phrase_time_limit=6):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 0.8
        audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    try:
        return r.recognize_google(audio, language='en-in')
    except Exception:
        return None


# ------------------- FEATURE IMPLEMENTATIONS -------------------

def open_app(app_name: str, log_fn=lambda s: None):
    app_name = app_name.lower().strip()
    path = DEFAULT_APPS.get(app_name)
    if path:
        log_fn(f'Opening {app_name}...')
        try:
            os.startfile(path)
        except Exception as e:
            log_fn(f'Could not open {app_name}: {e}')
    else:
        log_fn(f'Unknown app: {app_name}')


def tell_time(log_fn=lambda s: None):
    now = datetime.datetime.now().strftime('%I:%M %p')
    log_fn(f'Time: {now}')
    speak(f'The current time is {now}')


def tell_date(log_fn=lambda s: None):
    now = datetime.datetime.now().strftime('%A, %d %B %Y')
    log_fn(f'Date: {now}')
    speak(f'Today is {now}')


def play_random_music(log_fn=lambda s: None):
    try:
        if not MUSIC_FOLDER.exists():
            log_fn('Music folder not found. Please set your Music folder.')
            speak('Music folder not found.')
            return
        files = [f for f in os.listdir(MUSIC_FOLDER) if f.lower().endswith(('.mp3', '.wav', '.m4a', '.flac', '.aac', '.wma'))]
        if not files:
            log_fn('No music files found in Playlists folder.')
            speak('No music files found.')
            return
        choice = random.choice(files)
        path = MUSIC_FOLDER / choice
        log_fn(f'Playing: {choice}')
        os.startfile(path)
    except Exception as e:
        log_fn(f'Error playing music: {e}')


def take_screenshot(log_fn=lambda s: None):
    try:
        speak('Taking screenshot in 3 seconds. Please hold still.')
        log_fn('Screenshot in 3s...')
        time.sleep(3)
        img = pyautogui.screenshot()
        filename = Path.cwd() / f'screenshot_{int(time.time())}.png'
        img.save(filename)
        log_fn(f'Screenshot saved as {filename}')
        speak(f'Screenshot saved as {filename.name}')
    except Exception as e:
        log_fn(f'Screenshot failed: {e}')


def system_info(log_fn=lambda s: None):
    try:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        s = f'CPU: {cpu}% | RAM: {int(mem.percent)}%'
        if battery:
            s += f' | Battery: {int(battery.percent)}%'
        log_fn(s)
        speak('System status shown in UI.')
    except Exception as e:
        log_fn(f'Could not fetch system info: {e}')


def search_web(query: str, log_fn=lambda s: None):
    if not query:
        log_fn('Empty search query')
        return
    log_fn(f'Searching: {query}')
    wb.open('https://www.google.com/search?q=' + query.replace(' ', '+'))


def play_on_youtube(query: str, log_fn=lambda s: None):
    if not query:
        log_fn('Empty youtube query - opening YouTube home')
        wb.open('https://youtube.com')
        return
    log_fn(f'Playing on YouTube: {query}')
    try:
        pywhatkit.playonyt(query)
    except Exception:
        wb.open('https://www.youtube.com/results?search_query=' + query.replace(' ', '+'))


def tell_joke(log_fn=lambda s: None):
    joke = pyjokes.get_joke()
    log_fn(joke)
    speak(joke)


def shutdown_system(log_fn=lambda s: None):
    log_fn('Shutdown initiated (10 seconds)')
    speak('Shutting down in ten seconds. Save your work.')
    if os.name == 'nt':
        os.system('shutdown /s /t 10')
    else:
        os.system('shutdown -h +0')


def restart_system(log_fn=lambda s: None):
    log_fn('Restart initiated')
    speak('Restarting now.')
    if os.name == 'nt':
        os.system('shutdown /r /t 5')
    else:
        os.system('reboot')

# ------------------- GUI APP -------------------

class AssistantGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Desktop Voice Assistant')
        self.geometry('900x560')
        self.resizable(False, False)
        self.protocol('WM_DELETE_WINDOW', self.on_close)

        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        # Top frame: controls
        top = ttk.Frame(self, padding=8)
        top.pack(fill='x')

        self.command_var = tk.StringVar()
        entry = ttk.Entry(top, textvariable=self.command_var, width=70)
        entry.grid(row=0, column=0, padx=(0, 8))
        entry.bind('<Return>', lambda e: self.apply_text_command())

        btn_speak = ttk.Button(top, text='🎙️ Speak', command=self.on_speak_click)
        btn_speak.grid(row=0, column=1, padx=4)

        btn_run = ttk.Button(top, text='▶️ Run', command=self.on_run_click)
        btn_run.grid(row=0, column=2, padx=4)

        btn_help = ttk.Button(top, text='❓ Help', command=self.show_help)
        btn_help.grid(row=0, column=3, padx=4)

        # Middle frame: actions
        mid = ttk.Frame(self, padding=8)
        mid.pack(fill='x')

        ttk.Button(mid, text='Play Music', command=lambda: self.run_background(play_random_music)).grid(row=0, column=0, padx=6, pady=6)
        ttk.Button(mid, text='YouTube ▶', command=lambda: self.run_background(lambda log: play_on_youtube(self.command_var.get(), log))).grid(row=0, column=1, padx=6, pady=6)
        ttk.Button(mid, text='Search Web', command=lambda: self.run_background(lambda log: search_web(self.command_var.get(), log))).grid(row=0, column=2, padx=6, pady=6)
        ttk.Button(mid, text='Screenshot', command=lambda: self.run_background(take_screenshot)).grid(row=0, column=3, padx=6, pady=6)
        ttk.Button(mid, text='System Info', command=lambda: self.run_background(system_info)).grid(row=0, column=4, padx=6, pady=6)
        ttk.Button(mid, text='Tell Joke', command=lambda: self.run_background(tell_joke)).grid(row=0, column=5, padx=6, pady=6)

        # Lower frame: log and quick app open
        lower = ttk.Frame(self, padding=8)
        lower.pack(fill='both', expand=True)

        left = ttk.Frame(lower)
        left.pack(side='left', fill='both', expand=True)

        ttk.Label(left, text='Assistant Log').pack(anchor='w')
        self.logbox = tk.Text(left, height=22, state='disabled', wrap='word')
        self.logbox.pack(fill='both', expand=True, pady=(4, 0))

        right = ttk.Frame(lower, width=260)
        right.pack(side='right', fill='y')

        ttk.Label(right, text='Quick Apps').pack(anchor='w')
        for app in DEFAULT_APPS.keys():
            ttk.Button(right, text=app.title(), width=28, command=lambda a=app: self.run_background(lambda log: open_app(a, log))).pack(pady=4)

        ttk.Separator(right).pack(fill='x', pady=6)
        ttk.Button(right, text='Volume Up', width=28, command=lambda: self.change_volume('up')).pack(pady=4)
        ttk.Button(right, text='Volume Down', width=28, command=lambda: self.change_volume('down')).pack(pady=4)
        ttk.Button(right, text='Mute/Unmute', width=28, command=lambda: self.change_volume('mute')).pack(pady=4)
        ttk.Button(right, text='Set Brightness', width=28, command=lambda: self.prompt_brightness()).pack(pady=4)
        ttk.Button(right, text='Open File', width=28, command=lambda: self.handle_query('open file')).pack(pady=4)
        ttk.Button(right, text='Open Folder', width=28, command=lambda: self.handle_query('open folder')).pack(pady=4)
        ttk.Button(right, text='Save Log', width=28, command=lambda: self.save_log()).pack(pady=4)

        ttk.Separator(right).pack(fill='x', pady=6)
        ttk.Button(right, text='Shutdown', width=28, command=lambda: self.run_background(shutdown_system)).pack(pady=4)
        ttk.Button(right, text='Restart', width=28, command=lambda: self.run_background(restart_system)).pack(pady=4)
        ttk.Button(right, text='Always on Top', width=28, command=lambda: self.toggle_always_on_top()).pack(pady=4)
        ttk.Button(right, text='Exit', width=28, command=self.on_close).pack(pady=4)

        # Status bar
        self.status_var = tk.StringVar(value='Ready')
        status = ttk.Label(self, textvariable=self.status_var, relief='sunken', anchor='w')
        status.pack(side='bottom', fill='x')

        # Greet
        self.log('Welcome! Say "open youtube", "play music", "time", "date", "screenshot", "system info", "joke", "open notepad", or type a command and press Run.')
        speak('Hello! I am your desktop assistant. How can I help you?')

    # ---------------- UI helpers ----------------
    def log(self, text: str):
        ts = datetime.datetime.now().strftime('%H:%M:%S')
        self.logbox.configure(state='normal')
        self.logbox.insert('end', f'[{ts}] {text}\n')
        self.logbox.see('end')
        self.logbox.configure(state='disabled')

    def set_status(self, text: str):
        self.status_var.set(text)

    def run_background(self, fn):
        """Run a feature function in background thread so UI doesn't block."""
        def target():
            self.set_status('Working...')
            try:
                fn(lambda s: self.log(s))
            except Exception as e:
                self.log(f'Error: {e}')
            self.set_status('Ready')

        t = threading.Thread(target=target, daemon=True)
        t.start()

    # ---------------- Commands -----------------
    def apply_text_command(self):
        query = self.command_var.get().lower().strip()
        if not query:
            self.log('No command typed.')
            return
        self.log(f'Command: {query}')
        self.handle_query(query)

    def handle_query(self, query: str = None):
        """Process a typed or spoken query."""
        q = query if query is not None else self.command_var.get().lower().strip()
        q = (q or '').lower()
        if not q:
            self.log('Empty command received.')
            return
        self.log(f'Processing: {q}')

        # Basic command routing
        if 'open youtube' in q:
            self.run_background(lambda log: play_on_youtube(''))
        elif q.startswith('play ') and 'youtube' in q:
            # format: play <song> on youtube
            song = q.replace('play', '').replace('on youtube', '').strip()
            self.run_background(lambda log: play_on_youtube(song, log))
        elif 'play music' in q or 'play song' in q:
            self.run_background(play_random_music)
        elif 'time' == q or 'what is the time' in q or 'tell time' in q:
            self.run_background(tell_time)
        elif 'date' == q or 'today date' in q or 'what is the date' in q:
            self.run_background(tell_date)
        elif 'screenshot' in q:
            self.run_background(take_screenshot)
        elif 'system info' in q or 'status' in q:
            self.run_background(system_info)
        elif 'joke' in q:
            self.run_background(tell_joke)
        elif q.startswith('open '):
            app = q.replace('open', '').strip()
            self.run_background(lambda log: open_app(app, log))
        elif q.startswith('search '):
            term = q.replace('search', '').strip()
            self.run_background(lambda log: search_web(term, log))
        elif q.startswith('shutdown'):
            self.run_background(shutdown_system)
        elif q.startswith('restart'):
            self.run_background(restart_system)
        elif q.startswith('volume up'):
            self.change_volume('up')
        elif q.startswith('volume down'):
            self.change_volume('down')
        elif q.startswith('mute') or q.startswith('unmute'):
            self.change_volume('mute')
        elif q.startswith('brightness'):
            # example: "brightness 50" or "set brightness to 70"
            try:
                import re
                num = re.search(r"(\d{1,3})", q)
                if num:
                    val = int(num.group(1))
                    self.set_brightness(val)
                else:
                    self.log('Please say brightness value between 0 and 100.')
            except Exception as e:
                self.log(f'Brightness command failed: {e}')
        elif q.startswith('chat') or q.startswith('ask') or q.startswith('talk'):
            # simple chatbot mode: answer small talk or open web for unknown
            txt = q.replace('chat', '').replace('ask', '').replace('talk', '').strip()
            if not txt:
                self.log('You entered chat mode: say something like "chat how are you"')
                speak('I am ready to chat. Say something.')
            else:
                response = self.simple_chat_response(txt)
                self.log(f'Assistant: {response}')
                speak(response)
        elif q.startswith('open file') or q.startswith('open folder'):
            # open file/folder dialog
            path = filedialog.askopenfilename() if 'file' in q else filedialog.askdirectory()
            if path:
                try:
                    os.startfile(path)
                    self.log(f'Opened: {path}')
                except Exception as e:
                    self.log(f'Could not open {path}: {e}')
        elif q.startswith('remind me'):
            # format: remind me in 10 seconds to take a break
            try:
                import re
                m = re.search(r'in (\d+) (second|seconds|minute|minutes|hour|hours) to (.+)', q)
                if m:
                    num = int(m.group(1))
                    unit = m.group(2)
                    msg = m.group(3)
                    secs = num * (60 if 'minute' in unit else 3600 if 'hour' in unit else 1)
                    threading.Timer(secs, lambda: (speak(f'Reminder: {msg}'), self.log(f'Reminder fired: {msg}'))).start()
                    self.log(f'Reminder set for {num} {unit}: {msg}')
                else:
                    self.log('Could not parse reminder. Try: "remind me in 10 seconds to check oven"')
            except Exception as e:
                self.log(f'Reminder error: {e}')
        else:
            # fallback: try quick web search
            self.log('Command not recognized locally. Opening web search for query.')
            self.run_background(lambda log: search_web(q, log))

    def change_volume(self, mode: str):
        try:
            if mode == 'up':
                pyautogui.press('volumeup')
                self.log('Volume up (media key)')
            elif mode == 'down':
                pyautogui.press('volumedown')
                self.log('Volume down (media key)')
            else:
                pyautogui.press('volumemute')
                self.log('Toggled mute')
        except Exception as e:
            self.log(f'Volume control failed: {e}')

    def set_brightness(self, value: int):
        try:
            val = max(0, min(100, int(value)))
            # Try Windows WMI via powershell
            if os.name == 'nt':
                cmd = [
                    'powershell',
                    f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{val})"
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.log(f'Set brightness to {val}% (requested)')
            else:
                self.log('Brightness control not implemented on this OS.')
        except Exception as e:
            self.log(f'Brightness set failed: {e}')

    def simple_chat_response(self, text: str) -> str:
        # lightweight rule-based responses
        t = text.lower()
        if any(w in t for w in ('hi', 'hello', 'hey')):
            return 'Hello! How are you today?'
        if 'how are you' in t:
            return 'I am just code — but I am functioning perfectly. How can I help you?'
        if any(w in t for w in ('your name', 'who are you')):
            return 'I am your Desktop Assistant built with Python. You can ask me to open apps, play music, or take screenshots.'
        if 'joke' in t:
            return pyjokes.get_joke()
        # fallback small reply then offer search
        return 'I am not sure about that. Shall I search the web for you? Say "search <your question>".'

    # ---------------- UI callbacks ----------------
    def on_speak_click(self):
        self.set_status('Listening...')
        self.log('Listening for voice command...')
        def listen_and_handle():
            txt = recognize_speech()
            if txt:
                self.log(f'You said: {txt}')
                self.command_var.set(txt)
                self.handle_query(txt)
            else:
                self.log('Voice not recognized.')
                speak('Sorry, I did not get that.')
            self.set_status('Ready')
        threading.Thread(target=listen_and_handle, daemon=True).start()

    def on_run_click(self):
        txt = self.command_var.get().strip()
        if not txt:
            self.log('No command to run.')
            return
        self.handle_query(txt)

    def show_help(self):
        help_text = (
            'Try commands:\n'
            '- open youtube\n- play <song> on youtube\n- play music\n- time\n- date\n- screenshot\n- system info\n'
            '- open notepad\n- search <term>\n- chat <something>\n- volume up / volume down / mute\n- brightness <0-100>\n- remind me in 10 seconds to take a break\n'
        )
        messagebox.showinfo('Help', help_text)

    def prompt_brightness(self):
        val = tk.simpledialog.askinteger('Brightness', 'Enter brightness (0-100):', minvalue=0, maxvalue=100)
        if val is not None:
            self.set_brightness(val)

    def toggle_always_on_top(self):
        current = self.attributes('-topmost')
        self.attributes('-topmost', not current)
        self.log(f'Always on top set to {not current}')

    def save_log(self):
        txt = self.logbox.get('1.0', 'end').strip()
        if not txt:
            self.log('Nothing to save in log.')
            return
        p = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text', '*.txt')])
        if p:
            with open(p, 'w', encoding='utf-8') as f:
                f.write(txt)
            self.log(f'Log saved to {p}')

    def on_close(self):
        if messagebox.askokcancel('Quit', 'Do you really want to quit?'):
            try:
                engine.stop()
            except Exception:
                pass
            self.destroy()


# ----------------- MAIN -----------------

def main():
    app = AssistantGUI()
    app.mainloop()

if __name__ == '__main__':
    main()
