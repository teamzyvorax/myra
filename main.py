#!/usr/bin/env python3
"""MYRA — free Termux voice assistant starter for Android."""

from datetime import datetime
import json
import shutil
import subprocess
import sys
import time

APP_NAME = "MYRA"
SETTINGS_FILE = "settings.json"

PRESETS = {
    "male": {"pitch": "0.78", "rate": "0.92"},
    "female": {"pitch": "1.18", "rate": "1.00"},
}

def load_settings():
    defaults = {"voice": "male", "language": "en"}
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
        defaults.update(saved if isinstance(saved, dict) else {})
    except (OSError, json.JSONDecodeError):
        pass
    if defaults.get("voice") not in PRESETS:
        defaults["voice"] = "male"
    if defaults.get("language") not in ("en", "hi"):
        defaults["language"] = "en"
    return defaults

settings = load_settings()

def save_settings():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

def say(message):
    print(f"\n{APP_NAME}: {message}")
    if shutil.which("termux-tts-speak"):
        preset = PRESETS[settings["voice"]]
        lang = "hi-IN" if settings["language"] == "hi" else "en-US"
        try:
            subprocess.run(
                ["termux-tts-speak", "-l", lang, "-p", preset["pitch"],
                 "-r", preset["rate"], message],
                check=False, timeout=30, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (OSError, subprocess.TimeoutExpired):
            print("(TTS unavailable; showing text instead.)")
    else:
        print("(Install Termux:API to enable spoken replies.)")

def listen():
    if shutil.which("termux-speech-to-text"):
        try:
            result = subprocess.run(
                ["termux-speech-to-text"], capture_output=True, text=True,
                timeout=45, check=False,
            )
            phrase = result.stdout.strip()
            if phrase:
                print(f"You: {phrase}")
                return phrase.lower()
        except (OSError, subprocess.TimeoutExpired):
            pass
    return input("\nYou (type): ").strip().lower()

def run_api(command):
    if not shutil.which(command[0]):
        return None
    try:
        return subprocess.run(command, capture_output=True, text=True,
                              timeout=15, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None

def help_text():
    return ("Commands: help, time, battery, youtube, browser, voice, "
            "language, exit. You can also say hello.")

def handle(text):
    text = text.strip().lower()
    if not text:
        say("I did not hear that. Please try again." if settings["language"] == "en"
            else "मुझे सुनाई नहीं दिया। फिर से बोलिए।")
    elif text in ("exit", "quit", "stop", "बंद", "बंद करो"):
        say("Goodbye. MYRA going offline.")
        return False
    elif text in ("help", "commands", "मदद", "कमांड"):
        say(help_text())
    elif "time" in text or "समय" in text or "टाइम" in text:
        now = datetime.now().strftime("%I:%M %p")
        say("The time is " + now)
    elif "battery" in text or "बैटरी" in text:
        result = run_api(["termux-battery-status"])
        if result and result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                say(f"Battery is {data.get('percentage', 'unknown')} percent.")
            except json.JSONDecodeError:
                say("Battery information received, but could not be read.")
        else:
            say("Battery status needs the Termux API app and package.")
    elif "youtube" in text or "यूट्यूब" in text:
        run_api(["termux-open-url", "https://www.youtube.com"])
        say("Opening YouTube.")
    elif "browser" in text or "google" in text or "search" in text:
        run_api(["termux-open-url", "https://www.google.com"])
        say("Opening your browser.")
    elif text in ("voice", "change voice", "आवाज", "वॉइस"):
        settings["voice"] = "female" if settings["voice"] == "male" else "male"
        save_settings()
        say("Female-style voice selected." if settings["voice"] == "female"
            else "Male-style voice selected.")
    elif text in ("language", "भाषा"):
        settings["language"] = "hi" if settings["language"] == "en" else "en"
        save_settings()
        say("Hindi selected." if settings["language"] == "hi" else "English selected.")
    elif any(word in text for word in ("hello", "hi", "नमस्ते", "हेलो")):
        say("Hello! I am MYRA. How can I help you?")
    else:
        say("I can handle basic phone commands right now. Say help to hear the list.")
    return True

def main():
    print("\n╔══════════════════════════════╗")
    print("║       Z Y V O R A  /  MYRA   ║")
    print("║       PHONE VOICE ASSISTANT  ║")
    print("╚══════════════════════════════╝")
    say("Hello. MYRA is online. Say help for commands.")
    while True:
        try:
            if not handle(listen()):
                break
        except KeyboardInterrupt:
            say("MYRA stopped.")
            break

if __name__ == "__main__":
    main()
