#!/usr/bin/env python3
"""MYRA — free Termux voice assistant for Android."""

from datetime import datetime
import json
import shutil
import subprocess
import sys
from pathlib import Path

APP_NAME = "MYRA"
BASE_DIR = Path(__file__).resolve().parent
SETTINGS_FILE = BASE_DIR / "settings.json"
PRESETS = {
    "male": {"pitch": "0.82", "rate": "0.94"},
    "female": {"pitch": "1.12", "rate": "1.00"},
}

TEXT = {
    "en": {
        "online": "Hello. MYRA is online. Say help for commands.",
        "help": "Commands: help, time, battery, youtube, browser, male, female, hindi, english, voice, language, exit.",
        "hello": "Hello! I am MYRA. How can I help you?",
        "time": "The time is {value}.",
        "battery": "Battery is {value} percent.",
        "battery_error": "Battery status needs the Termux API app and package.",
        "youtube": "Opening YouTube.",
        "browser": "Opening Google in your browser.",
        "voice_male": "Male-style voice preset selected.",
        "voice_female": "Female-style voice preset selected.",
        "lang_hi": "Hindi selected.",
        "lang_en": "English selected.",
        "unknown": "I can handle basic phone commands right now. Say help for the command list.",
        "empty": "I did not hear that. Please try again.",
        "bye": "Goodbye. MYRA going offline.",
    },
    "hi": {
        "online": "नमस्ते। MYRA चालू है। कमांड सुनने के लिए हेल्प बोलिए।",
        "help": "कमांड: हेल्प, टाइम, बैटरी, यूट्यूब, ब्राउज़र, मेल, फीमेल, हिंदी, इंग्लिश और एग्जिट।",
        "hello": "नमस्ते! मैं MYRA हूँ। बताइए, क्या मदद करूँ?",
        "time": "अभी समय है {value}।",
        "battery": "बैटरी {value} प्रतिशत है।",
        "battery_error": "बैटरी जानकारी के लिए Termux API ऐप और पैकेज चाहिए।",
        "youtube": "यूट्यूब खोल रही हूँ।",
        "browser": "ब्राउज़र में गूगल खोल रही हूँ।",
        "voice_male": "मेल वॉइस प्रीसेट चुना गया।",
        "voice_female": "फीमेल वॉइस प्रीसेट चुना गया।",
        "lang_hi": "हिंदी चुनी गई।",
        "lang_en": "इंग्लिश चुनी गई।",
        "unknown": "मैं अभी बेसिक फोन कमांड कर सकती हूँ। कमांड सुनने के लिए हेल्प बोलिए।",
        "empty": "आवाज़ समझ नहीं आई। फिर से बोलिए।",
        "bye": "अलविदा। MYRA बंद हो रही है।",
    },
}

def load_settings():
    defaults = {"voice": "male", "language": "en"}
    try:
        saved = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        if isinstance(saved, dict):
            defaults.update(saved)
    except (OSError, json.JSONDecodeError):
        pass
    if defaults.get("voice") not in PRESETS:
        defaults["voice"] = "male"
    if defaults.get("language") not in TEXT:
        defaults["language"] = "en"
    return defaults

settings = load_settings()

def save_settings():
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")

def say(key, **values):
    message = TEXT[settings["language"]].get(key, key).format(**values)
    print(f"\n{APP_NAME}: {message}", flush=True)
    executable = shutil.which("termux-tts-speak")
    if not executable:
        print("(TTS unavailable: install Termux:API.)")
        return
    preset = PRESETS[settings["voice"]]
    language = "hi-IN" if settings["language"] == "hi" else "en-US"
    try:
        subprocess.run(
            [executable, "-l", language, "-p", preset["pitch"], "-r",
             preset["rate"], message],
            check=False, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        print("(Could not start Android text-to-speech.)")

def listen():
    executable = shutil.which("termux-speech-to-text")
    if executable:
        try:
            result = subprocess.run(
                [executable], capture_output=True, text=True,
                timeout=45, check=False,
            )
            phrase = result.stdout.strip()
            if phrase:
                print(f"You: {phrase}", flush=True)
                return phrase.lower()
        except (OSError, subprocess.TimeoutExpired):
            print("(Speech input unavailable; switching to typed input.)")
    return input("\nYou (type): ").strip().lower()

def run_api(*command):
    executable = shutil.which(command[0])
    if not executable:
        return None
    try:
        return subprocess.run(
            [executable, *command[1:]], capture_output=True,
            text=True, timeout=15, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

def set_voice(voice):
    settings["voice"] = voice
    save_settings()
    say("voice_" + voice)

def set_language(language):
    settings["language"] = language
    save_settings()
    say("lang_hi" if language == "hi" else "lang_en")

def handle(phrase):
    phrase = phrase.strip().lower()
    if not phrase:
        say("empty")
    elif phrase in ("exit", "quit", "stop", "बंद", "बंद करो", "एग्जिट"):
        say("bye")
        return False
    elif phrase in ("help", "commands", "मदद", "हेल्प", "कमांड"):
        say("help")
    elif phrase in ("male", "man voice", "मेल", "पुरुष आवाज"):
        set_voice("male")
    elif phrase in ("female", "woman voice", "फीमेल", "महिला आवाज"):
        set_voice("female")
    elif phrase in ("voice", "change voice", "आवाज", "वॉइस"):
        set_voice("female" if settings["voice"] == "male" else "male")
    elif phrase in ("hindi", "हिंदी"):
        set_language("hi")
    elif phrase in ("english", "इंग्लिश", "अंग्रेजी"):
        set_language("en")
    elif phrase in ("language", "भाषा"):
        set_language("hi" if settings["language"] == "en" else "en")
    elif "time" in phrase or "समय" in phrase or "टाइम" in phrase:
        say("time", value=datetime.now().strftime("%I:%M %p"))
    elif "battery" in phrase or "बैटरी" in phrase:
        result = run_api("termux-battery-status")
        try:
            data = json.loads(result.stdout) if result and result.returncode == 0 else {}
            if "percentage" in data:
                say("battery", value=data["percentage"])
            else:
                say("battery_error")
        except json.JSONDecodeError:
            say("battery_error")
    elif "youtube" in phrase or "यूट्यूब" in phrase:
        result = run_api("termux-open-url", "https://www.youtube.com")
        say("youtube" if result and result.returncode == 0 else "unknown")
    elif any(word in phrase for word in ("browser", "google", "search", "ब्राउज़र", "गूगल")):
        result = run_api("termux-open-url", "https://www.google.com")
        say("browser" if result and result.returncode == 0 else "unknown")
    elif any(word in phrase for word in ("hello", "hi", "नमस्ते", "हेलो")):
        say("hello")
    else:
        say("unknown")
    return True

def diagnostics():
    print("\nMYRA SYSTEM CHECK")
    for command in ("termux-speech-to-text", "termux-tts-speak",
                    "termux-battery-status", "termux-open-url"):
        print(f"{command}: {'FOUND' if shutil.which(command) else 'MISSING'}")
    print(f"Voice preset: {settings['voice']}")
    print(f"Language: {settings['language']}")
    print("Note: install the Termux:API Android app and grant microphone permission.")

def main():
    if "--check" in sys.argv:
        diagnostics()
        return
    print("\n╔══════════════════════════════╗")
    print("║       Z Y V O R A  /  MYRA   ║")
    print("║       PHONE VOICE ASSISTANT  ║")
    print("╚══════════════════════════════╝")
    say("online")
    while True:
        try:
            if not handle(listen()):
                break
        except (KeyboardInterrupt, EOFError):
            say("bye")
            break

if __name__ == "__main__":
    main()
