#!/usr/bin/env python3
"""MYRA — free Termux voice assistant for Android."""

from datetime import datetime
import ast
import json
import operator
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path

APP_NAME = "MYRA"
BASE_DIR = Path(__file__).resolve().parent
SETTINGS_FILE = BASE_DIR / "settings.json"
NOTES_FILE = BASE_DIR / "notes.json"
PRESETS = {
    "male": {"pitch": "0.82", "rate": "0.94"},
    "female": {"pitch": "1.12", "rate": "1.00"},
}
TIMERS = []
OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
    ast.Pow: operator.pow, ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}
TEXT = {
    "en": {
        "online": "Hello. MYRA is online. Say help for commands.",
        "help": "Commands: time, date, battery, calculator, note followed by text, show notes, timer followed by minutes, YouTube, browser, male, female, Hindi, English, help, exit.",
        "hello": "Hello! I am MYRA. How can I help you?",
        "time": "The time is {value}.", "date": "Today is {value}.",
        "battery": "Battery is {value} percent.",
        "battery_error": "Battery status needs the Termux API app and package.",
        "youtube": "Opening YouTube.", "browser": "Opening Google in your browser.",
        "voice_male": "Male-style voice preset selected.",
        "voice_female": "Female-style voice preset selected.",
        "lang_hi": "Hindi selected.", "lang_en": "English selected.",
        "unknown": "I cannot do that yet. Say help for available commands.",
        "empty": "I did not hear that. Please try again.",
        "bye": "Goodbye. MYRA going offline.",
        "note_saved": "Note saved.", "notes_empty": "You have no saved notes.",
        "notes_title": "Your saved notes:", "note_usage": "Say note followed by your note.",
        "timer_set": "Timer set for {minutes} minutes.",
        "timer_done": "Your timer is finished.",
        "timer_usage": "Say timer followed by a number of minutes.",
        "calc_error": "I could not calculate that. Try a simple arithmetic expression.",
        "calc_result": "The answer is {answer}.",
    },
    "hi": {
        "online": "नमस्ते। MYRA चालू है। कमांड सुनने के लिए हेल्प बोलिए।",
        "help": "कमांड: टाइम, तारीख, बैटरी, कैलकुलेटर, नोट के बाद अपना नोट, नोट्स दिखाओ, टाइमर के बाद मिनट, यूट्यूब, ब्राउज़र, मेल, फीमेल, हिंदी, इंग्लिश, हेल्प और एग्जिट।",
        "hello": "नमस्ते! मैं MYRA हूँ। बताइए, क्या मदद करूँ?",
        "time": "अभी समय है {value}।", "date": "आज तारीख {value} है।",
        "battery": "बैटरी {value} प्रतिशत है।",
        "battery_error": "बैटरी जानकारी के लिए Termux API ऐप और पैकेज चाहिए।",
        "youtube": "यूट्यूब खोल रही हूँ।", "browser": "ब्राउज़र में गूगल खोल रही हूँ।",
        "voice_male": "मेल वॉइस प्रीसेट चुना गया।",
        "voice_female": "फीमेल वॉइस प्रीसेट चुना गया।",
        "lang_hi": "हिंदी चुनी गई।", "lang_en": "इंग्लिश चुनी गई।",
        "unknown": "यह कमांड अभी उपलब्ध नहीं है। कमांड सुनने के लिए हेल्प बोलिए।",
        "empty": "आवाज़ समझ नहीं आई। फिर से बोलिए।",
        "bye": "अलविदा। MYRA बंद हो रही है।",
        "note_saved": "नोट सेव हो गया।", "notes_empty": "आपके कोई सेव नोट्स नहीं हैं।",
        "notes_title": "आपके सेव नोट्स:", "note_usage": "नोट बोलकर उसके बाद अपना नोट बताइए।",
        "timer_set": "{minutes} मिनट का टाइमर शुरू हो गया।",
        "timer_done": "आपका टाइमर पूरा हो गया।",
        "timer_usage": "टाइमर बोलकर मिनट की संख्या बताइए।",
        "calc_error": "हिसाब नहीं हो पाया। आसान गणित का सवाल बोलिए।",
        "calc_result": "जवाब है {answer}।",
    },
}

def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default

settings = load_json(SETTINGS_FILE, {"voice": "male", "language": "en"})
if settings.get("voice") not in PRESETS:
    settings["voice"] = "male"
if settings.get("language") not in TEXT:
    settings["language"] = "en"

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
        subprocess.run([executable, "-l", language, "-p", preset["pitch"],
                        "-r", preset["rate"], message],
                       check=False, timeout=30, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired):
        print("(Could not start Android text-to-speech.)")

def listen():
    executable = shutil.which("termux-speech-to-text")
    if executable:
        try:
            result = subprocess.run([executable], capture_output=True,
                                    text=True, timeout=45, check=False)
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
        return subprocess.run([executable, *command[1:]], capture_output=True,
                              text=True, timeout=15, check=False)
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

def save_note(note):
    notes = load_json(NOTES_FILE, [])
    if not isinstance(notes, list):
        notes = []
    notes.append({"text": note, "created": datetime.now().isoformat(timespec="minutes")})
    NOTES_FILE.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")
    say("note_saved")

def show_notes():
    notes = load_json(NOTES_FILE, [])
    if not notes:
        say("notes_empty")
        return
    say("notes_title")
    for index, item in enumerate(notes[-20:], 1):
        print(f"{index}. {item.get('text', '')} [{item.get('created', '')}]")

def safe_calculate(expression):
    expression = expression.replace("×", "*").replace("÷", "/").replace("^", "**")
    tree = ast.parse(expression, mode="eval")
    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            left, right = evaluate(node.left), evaluate(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 8:
                raise ValueError("Exponent too large")
            result = OPS[type(node.op)](left, right)
            if abs(result) > 10**15:
                raise ValueError("Result too large")
            return result
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
            return OPS[type(node.op)](evaluate(node.operand))
        raise ValueError("Unsupported expression")
    return evaluate(tree)

def start_timer(minutes, reminder=None):
    seconds = minutes * 60
    def finished():
        if reminder:
            print(f"\nMYRA REMINDER: {reminder}", flush=True)
            say("timer_done")
            say(reminder)
        else:
            say("timer_done")
    timer = threading.Timer(seconds, finished)
    timer.daemon = True
    timer.start()
    TIMERS.append(timer)
    say("timer_set", minutes=minutes)

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
    elif phrase.startswith(("note ", "नोट ")):
        note = phrase.split(" ", 1)[1].strip()
        if note:
            save_note(note)
        else:
            say("note_usage")
    elif phrase in ("show notes", "list notes", "मेरे नोट्स दिखाओ", "नोट्स दिखाओ", "नोट दिखाओ"):
        show_notes()
    elif phrase.startswith(("timer ", "टाइमर ")):
        match = re.search(r"(\d+)", phrase)
        if match and 0 < int(match.group(1)) <= 1440:
            start_timer(int(match.group(1)))
        else:
            say("timer_usage")
    elif phrase.startswith(("calculate ", "calculator ", "गणना ")):
        expression = re.sub(r"^(calculate|calculator|गणना)\s+", "", phrase)
        try:
            answer = safe_calculate(expression)
            say("calc_result", answer=answer)
        except (ValueError, SyntaxError, ZeroDivisionError, OverflowError):
            say("calc_error")
    elif "time" in phrase or "समय" in phrase or "टाइम" in phrase:
        say("time", value=datetime.now().strftime("%I:%M %p"))
    elif "date" in phrase or "तारीख" in phrase:
        say("date", value=datetime.now().strftime("%d %B %Y"))
    elif "battery" in phrase or "बैटरी" in phrase:
        result = run_api("termux-battery-status")
        try:
            data = json.loads(result.stdout) if result and result.returncode == 0 else {}
            say("battery", value=data["percentage"]) if "percentage" in data else say("battery_error")
        except (json.JSONDecodeError, TypeError):
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
    print("Termux:API Android app and microphone permission are required for voice.")

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
