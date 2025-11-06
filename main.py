import pyttsx3
import datetime
import speech_recognition as sr
import webbrowser as wb
import os
import random
import pywhatkit
import pyautogui
import time
import psutil
import pyjokes
from pathlib import Path

name="bhatt"

# ------------------- INITIAL SETUP -------------------
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id) # pyright: ignore[reportIndexIssue]

def speak(text):
    print(f"Desktop Assistant :{text}")
    engine.say(text)
    engine.runAndWait()

# ------------------- GREETING -------------------
def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour < 12:
        speak("Good morning Sir, I am Your Desktop Assistant. How Can I help you")
    elif hour < 18:
        speak("Good afternoon Sir, I am Your Desktop Assistant. How Can I help you")
    else:
        speak("Good evening Sir, I am Your Desktop Assistant. How Can I help you")
    speak("Ask Me Question Like\nOpen Youtube\nPlay Music\nWhat is weather\nGive System Info\nTell me a joke\nWhat is time/date...\n---Speak Now---\n\n")

# ------------------- VOICE INPUT -------------------
def takeCommand():
    """Takes voice input from the user."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎧 Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in') # pyright: ignore[reportAttributeAccessIssue]
        print(f"🗣️ You said: {query}")
    except Exception:
        speak("Sorry, I didn’t catch that. Please say it again.")
        return "none"
    return query.lower()

# ------------------- FEATURE FUNCTIONS -------------------

def openApp(app_name):
    paths = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "vscode": f"C:\\Users\\{name}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
    }
    if app_name in paths:
        speak(f"Okay, opening {app_name}.")
        os.startfile(paths[app_name])
    else:
        speak(f"Sorry, I don't know where {app_name} is installed.")

def tellTime():
    strTime = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The current time is {strTime}")

def tellDate():
    strDate = datetime.datetime.now().strftime("%A, %d %B %Y")
    speak(f"Today's date is {strDate}")

def playMusic():
    """Play a random song from the user's Music/Playlists folder."""
    music_dir = Path.home() / "Music" / "Playlists"
    valid_exts = (".mp3", ".wav", ".m4a", ".flac", ".aac", ".wma")

    try:
        if not music_dir.exists():
            speak("Your music folder does not exist.")
            return

        songs = [f for f in os.listdir(music_dir) if f.lower().endswith(valid_exts)]
        if not songs:
            speak("No music files found in your Playlists folder.")
            return

        song = random.choice(songs)
        song_path = os.path.join(music_dir, song)
        speak(f"Playing {song}.")
        os.startfile(song_path)  # ✅ fixed line

    except Exception as e:
        speak("I couldn't play music due to an error.")
        print("❌ Error:", e)

def systemInfo():
    cpu = psutil.cpu_percent()
    battery = psutil.sensors_battery()
    speak("Here's your system status.")
    speak(f"CPU usage is at {cpu} percent.")
    if battery:
        speak(f"Battery is at {battery.percent} percent.")
    else:
        speak("I couldn't retrieve battery information.")

def takeScreenshot():
    speak("Sure! Taking a screenshot in three seconds. Please hold still.")
    time.sleep(3)
    img = pyautogui.screenshot()
    filename = f"screenshot_{int(time.time())}.png"
    img.save(filename)
    speak(f"Screenshot saved as {filename}.")

# ------------------- MAIN PROGRAM -------------------
if __name__ == "__main__":
    wishMe()

    while True:
        query = takeCommand()

        if "open youtube" in query:
            speak("Okay, opening YouTube.")
            wb.open("https://youtube.com")

        elif "open google" in query:
            speak("Alright, opening Google.")
            wb.open("https://google.com")

        elif "play" in query and ("youtube" in query or "Youtube" in query):
            song = query.replace("play", "").replace("on youtube", "").strip()
            speak(f"Sure, playing {song} on YouTube.")
            try:
                import pywhatkit
                pywhatkit.playonyt(song) # type: ignore
            except Exception:
                import urllib.parse
                wb.open("https://www.youtube.com/results?search_query=" + urllib.parse.quote(song))

        elif "play music" in query or "play song" in query:
            playMusic()

        elif "time" in query:
            tellTime()

        elif "date" in query:
            tellDate()

        elif "joke" in query:
            speak("Here's a joke for you.")
            speak(pyjokes.get_joke())

        elif "screenshot" in query:
            takeScreenshot()

        elif "system info" in query or "status" in query:
            systemInfo()

        elif "open" in query:
            app = query.replace("open", "").strip()
            openApp(app)

        elif "search" in query:
            search_query = query.replace("search", "").strip()
            speak(f"Sure, searching for {search_query} on Google.")
            pywhatkit.search(search_query) # type: ignore

        elif "weather" in query:
            speak("Alright, showing today's weather forecast.")
            wb.open("https://www.google.com/search?q=weather")

        elif "shutdown" in query:
            speak("Shutting down your system in ten seconds.")
            os.system("shutdown /s /t 10")

        elif "restart" in query:
            speak("Restarting your computer now.")
            os.system("shutdown /r /t 5")

        elif "exit" in query or "quit" in query or "stop" in query:
            speak("Goodbye! Have a great day ahead.")
            break

        else:
            speak("Sorry, I didn't understand that command. Please try again.")
