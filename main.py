#!/usr/bin/env python3
"""MYRA — free Termux voice assistant for Android."""

from datetime import datetime
import ast
import json
import operator
import random
import re
import time
import shutil
import subprocess
import sys
import threading
from urllib.parse import quote
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
PENDING_ACTION = None
STOPWATCH_START = None
APP_PACKAGES = {"whatsapp":"com.whatsapp","chrome":"com.android.chrome","youtube":"com.google.android.youtube","settings":"com.android.settings","maps":"com.google.android.apps.maps","gmail":"com.google.android.gm"}
SETTINGS_ACTIONS = {
    "wifi": "android.settings.WIFI_SETTINGS",
    "bluetooth": "android.settings.BLUETOOTH_SETTINGS",
    "display": "android.settings.DISPLAY_SETTINGS",
    "sound": "android.settings.SOUND_SETTINGS",
    "apps": "android.settings.APPLICATION_SETTINGS",
    "security": "android.settings.SECURITY_SETTINGS",
    "speech": "android.settings.SPEECH_SETTINGS",
}
AUDIO_EXTENSIONS = {".mp3", ".m4a", ".wav", ".ogg", ".flac", ".opus", ".aac"}
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
        "help": "Commands: time, date, battery, volume up/down, volume music 70, brightness 120, play music song.mp3, play love song, open youtuber NAME, open streamer NAME, youtube search QUERY, open live stream NAME, scroll up/down, go back, like video, open comments, type comment TEXT, lock phone, pause/resume/stop music, notify message, open settings wifi/bluetooth/display/sound/apps/security/speech, flashlight on/off, vibrate, search words, calculate 12 * 8, note text, timer 5, remind 5 drink water, open app APP NAME (opens installed app or Play Store search), camera (photo scan + live vision), contacts, call/SMS with confirmation, wifi, bluetooth, help, exit.",
        "hello": "Hello! I am MYRA. How can I help you?",
        "time": "The time is {value}.", "date": "Today is {value}.",
        "battery": "Battery is {value} percent.",
        "battery_error": "Battery status needs the Termux API app and package.",
        "youtube": "Opening YouTube.", "youtube_search": "Searching YouTube for {query}.", "browser": "Opening Google in your browser.",
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
        "reminder_set": "Reminder set for {minutes} minutes: {message}.",
        "random_result": "Your random number is {number}.",
        "stopwatch_started": "Stopwatch started.", "stopwatch_result": "Elapsed time: {seconds} seconds.",
        "stopwatch_idle": "Stopwatch is not running.",
        "volume_set": "The {stream} volume is now {level}.",
        "volume_usage": "Say volume music 8, or volume up or volume down.",
        "brightness_set": "Screen brightness set to {level}.",
        "brightness_usage": "Say brightness followed by a number from 0 to 255.",
        "media_usage": "Say play music followed by a file name, pause music, resume music, or stop music.",
        "love_song": "Finding a random romantic song on YouTube.",
        "media_started": "Starting music.",
        "media_done": "Media command completed.",
        "media_error": "Could not control music. Check the file and Termux:API.",
        "notification_done": "Notification sent.",
        "settings_open": "Opening {setting} settings.",
        "settings_error": "Could not open that settings page.",
        "wifi_error": "Wi-Fi information is unavailable. Check Termux:API and permissions.",
        "bluetooth_error": "Bluetooth information is unavailable. Check Termux:API and permissions.",
        "battery_details": "Here are the battery details.",
        "calc_error": "I could not calculate that. Try a simple arithmetic expression.",
        "calc_result": "The answer is {answer}.",
        "torch_on": "Flashlight turned on.", "torch_off": "Flashlight turned off.",
        "torch_error": "Flashlight control is unavailable. Check Termux API.",
        "vibrate": "Vibrating the phone.", "vibrate_error": "Vibration is unavailable.",
        "search": "Searching the web for {query}.",
        "contacts_error": "Could not read contacts. Check Termux:API permissions.",
        "contacts_none": "No matching contacts found.", "contacts_title": "Matching contacts:",
        "call_confirm": "Call {number}? Say confirm to place the call, or cancel.",
        "sms_confirm": "Send this message to {number}: {message}. Say confirm to send, or cancel.",
        "action_cancelled": "Action cancelled.", "action_done": "Action completed.",
        "action_error": "Action failed. Check permissions and Termux:API.",
        "app_open": "Opening {app}.", "app_unknown": "That app is not in MYRA safe launch list.",
        "call_usage": "Say call followed by a phone number.", "sms_usage": "Say sms, number, then message.",
    },
    "hi": {
        "online": "नमस्ते। MYRA चालू है। कमांड सुनने के लिए हेल्प बोलिए।",
        "help": "कमांड: टाइम, तारीख, बैटरी, वॉल्यूम बढ़ाओ/कम करो, वॉल्यूम म्यूजिक 70, ब्राइटनेस 120, गाना चलाओ song.mp3, लव सॉन्ग चलाओ, यूट्यूबर खोलो NAME, यूट्यूब पर खोजो QUERY, लाइव स्ट्रीम खोलो NAME, ऊपर/नीचे स्क्रॉल, पीछे जाओ, वीडियो लाइक करो, कमेंट खोलो, कमेंट लिखो TEXT, फोन लॉक करो, म्यूजिक पॉज/चालू/बंद, नोटिफिकेशन संदेश, सेटिंग खोलो wifi/bluetooth/display/sound/apps/speech, टॉर्च, वाइब्रेट, सर्च, नोट, टाइमर, रिमाइंडर, कैमरा खोलो (फोटो और लाइव विजन), ऐप खोलो, कॉन्टैक्ट, कॉल/SMS कन्फर्मेशन के साथ, हेल्प, एग्जिट।",
        "hello": "नमस्ते! मैं MYRA हूँ। बताइए, क्या मदद करूँ?",
        "time": "अभी समय है {value}।", "date": "आज तारीख {value} है।",
        "battery": "बैटरी {value} प्रतिशत है।",
        "battery_error": "बैटरी जानकारी के लिए Termux API ऐप और पैकेज चाहिए।",
        "youtube": "यूट्यूब खोल रही हूँ।", "youtube_search": "YouTube पर {query} खोज रही हूँ।", "browser": "ब्राउज़र में गूगल खोल रही हूँ।",
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
        "reminder_set": "{minutes} मिनट बाद रिमाइंडर: {message}।",
        "random_result": "आपका रैंडम नंबर है {number}।",
        "stopwatch_started": "स्टॉपवॉच शुरू हो गई।", "stopwatch_result": "बीता समय {seconds} सेकंड है।",
        "stopwatch_idle": "स्टॉपवॉच चालू नहीं है।",
        "volume_set": "{stream} वॉल्यूम अब {level} है।",
        "volume_usage": "वॉल्यूम म्यूजिक 8, वॉल्यूम बढ़ाओ या वॉल्यूम कम करो बोलें।",
        "brightness_set": "स्क्रीन ब्राइटनेस {level} कर दी।",
        "brightness_usage": "ब्राइटनेस के बाद 0 से 255 तक नंबर बोलें।",
        "media_usage": "प्ले म्यूजिक के बाद फाइल का नाम, पॉज म्यूजिक, रिज्यूम म्यूजिक या स्टॉप म्यूजिक बोलें।",
        "love_song": "आपके लिए एक रैंडम रोमांटिक गाना YouTube पर खोल रही हूँ।",
        "media_started": "म्यूजिक शुरू कर रही हूँ।",
        "media_done": "मीडिया कमांड पूरा हुआ।",
        "media_error": "म्यूजिक कंट्रोल नहीं हुआ। फाइल और Termux API चेक करें।",
        "notification_done": "नोटिफिकेशन भेज दिया।",
        "settings_open": "{setting} सेटिंग्स खोल रही हूँ।",
        "settings_error": "यह सेटिंग्स पेज नहीं खुल पाया।",
        "wifi_error": "वाईफाई जानकारी उपलब्ध नहीं है। Termux API चेक करें।",
        "bluetooth_error": "ब्लूटूथ जानकारी उपलब्ध नहीं है। Termux API चेक करें।",
        "battery_details": "बैटरी की पूरी जानकारी यह है।",
        "calc_error": "हिसाब नहीं हो पाया। आसान गणित का सवाल बोलिए।",
        "calc_result": "जवाब है {answer}।",
        "torch_on": "फोन की टॉर्च चालू हो गई।", "torch_off": "फोन की टॉर्च बंद हो गई।",
        "torch_error": "टॉर्च कंट्रोल उपलब्ध नहीं है। Termux API चेक करें।",
        "vibrate": "फोन वाइब्रेट हो रहा है।", "vibrate_error": "वाइब्रेशन उपलब्ध नहीं है।",
        "search": "{query} के लिए इंटरनेट पर खोज रही हूँ।",
        "contacts_error": "कॉन्टैक्ट नहीं पढ़ पाए। Termux API परमिशन चेक करें।",
        "contacts_none": "इस नाम का कॉन्टैक्ट नहीं मिला।", "contacts_title": "मिले हुए कॉन्टैक्ट:",
        "call_confirm": "{number} पर कॉल करना है? कन्फर्म बोलें या कैंसल।",
        "sms_confirm": "{number} पर यह मैसेज भेजना है: {message}। कन्फर्म बोलें या कैंसल।",
        "action_cancelled": "एक्शन कैंसल कर दिया।", "action_done": "एक्शन पूरा हुआ।",
        "action_error": "एक्शन नहीं हुआ। परमिशन और Termux API चेक करें।",
        "app_open": "{app} खोल रही हूँ।", "app_unknown": "यह ऐप सुरक्षित लिस्ट में नहीं है।",
        "call_usage": "कॉल बोलकर फोन नंबर बताइए।", "sms_usage": "एसएमएस बोलकर नंबर और मैसेज बताइए।",
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
    if reminder:
        say("reminder_set", minutes=minutes, message=reminder)
    else:
        say("timer_set", minutes=minutes)


def list_contacts(query=""):
    result = run_api("termux-contact-list")
    if not result or result.returncode != 0:
        say("contacts_error")
        return
    try:
        contacts = json.loads(result.stdout)
    except json.JSONDecodeError:
        say("contacts_error")
        return
    found = []
    for contact in contacts:
        name = str(contact.get("name", ""))
        if query in name.lower():
            for item in contact.get("number", []):
                number = item.get("number", "") if isinstance(item, dict) else str(item)
                if number:
                    found.append((name, number))
    if not found:
        say("contacts_none")
    else:
        say("contacts_title")
        for name, number in found[:10]:
            print(f"{name}: {number}")

def launch_app(app):
    app = app.strip()[:80]
    package = APP_PACKAGES.get(app.lower())
    if package:
        result = run_api("monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1")
        if result and result.returncode == 0:
            say("app_open", app=app)
            return
    if companion_command("open_app", app):
        say("app_open", app=app)
    else:
        say("action_error")

def set_volume(stream, level):
    allowed = {"music", "ring", "alarm", "notification", "system", "call"}
    if stream not in allowed or not 0 <= level <= 100:
        return False
    result = run_api("termux-volume")
    if not result or result.returncode != 0:
        return False
    try:
        data = json.loads(result.stdout)
        entries = data if isinstance(data, list) else data.get("streams", [])
        item = next((x for x in entries if str(x.get("stream", "")).lower() == stream), None)
        if item:
            maximum = int(item.get("max_volume", 15))
            actual = round(maximum * level / 100) if level <= 100 else level
            actual = max(0, min(maximum, actual))
        else:
            actual = max(0, min(15, round(15 * level / 100)))
        changed = run_api("termux-volume", stream, str(actual))
        return bool(changed and changed.returncode == 0), actual
    except (ValueError, TypeError, json.JSONDecodeError):
        return False, None

def change_volume(direction):
    result = run_api("termux-volume")
    if not result or result.returncode != 0:
        return False, None
    try:
        data = json.loads(result.stdout)
        entries = data if isinstance(data, list) else data.get("streams", [])
        item = next((x for x in entries if str(x.get("stream", "")).lower() == "music"), None)
        if not item:
            return False, None
        maximum = int(item.get("max_volume", 15))
        current = int(item.get("volume", 0))
        target = max(0, min(maximum, current + direction * max(1, round(maximum * 0.08))))
        changed = run_api("termux-volume", "music", str(target))
        return bool(changed and changed.returncode == 0), target
    except (ValueError, TypeError, json.JSONDecodeError):
        return False, None

def play_music(filename):
    candidate = Path(filename).expanduser()
    music_dir = Path.home() / "storage" / "music"
    if not candidate.is_absolute():
        candidate = music_dir / candidate
    try:
        resolved = candidate.resolve(strict=True)
        allowed_roots = [music_dir.resolve(), BASE_DIR.resolve()]
        if not any(resolved == root or root in resolved.parents for root in allowed_roots):
            return False
        if not resolved.is_file() or resolved.suffix.lower() not in AUDIO_EXTENSIONS:
            return False
    except (OSError, RuntimeError):
        return False
    result = run_api("termux-media-player", "play", str(resolved))
    return bool(result and result.returncode == 0)

def open_settings_page(setting):
    action = SETTINGS_ACTIONS.get(setting)
    if not action:
        return False
    result = run_api("am", "start", "-a", action)
    return bool(result and result.returncode == 0)

def play_random_love_song():
    choices = ["Tum Hi Ho Arijit Singh", "Raabta Arijit Singh", "Kesariya Brahmastra", "Hawayein Arijit Singh", "Apna Bana Le Arijit Singh", "Tera Hone Laga Hoon Atif Aslam", "Raatan Lambiyan Jubin Nautiyal", "Shayad Arijit Singh"]
    query = random.choice(choices)
    url = "https://www.youtube.com/results?search_query=" + quote(query)
    result = run_api("termux-open-url", url)
    return bool(result and result.returncode == 0)

def open_youtube_search(query, live=False):
    query = query.strip()[:180]
    if not query:
        return False
    if live:
        query += " live stream"
    url = "https://www.youtube.com/results?search_query=" + quote(query)
    result = run_api("termux-open-url", url)
    return bool(result and result.returncode == 0)

def companion_command(command, text=""):
    allowed = {"scroll_up", "scroll_down", "back", "like", "open_comments", "lock_screen", "type_comment", "open_app", "camera"}
    if command not in allowed or not shutil.which("am"):
        return False
    args = ["am", "start", "-n", "com.zyvora.myra/.CommandActivity", "--es", "command", command]
    if text:
        args += ["--es", "text", text[:500]]
    result = run_api(*args)
    return bool(result and result.returncode == 0)

def send_notification(message):
    message = message.strip()[:500]
    if not message:
        return False
    result = run_api("termux-notification", "--title", "MYRA", "--content", message, "--priority", "high")
    return bool(result and result.returncode == 0)

def handle(phrase):
    global PENDING_ACTION
    phrase = phrase.strip().lower()
    if PENDING_ACTION:
        if phrase in ("confirm", "yes", "हाँ", "हां", "कन्फर्म", "पक्का"):
            action = PENDING_ACTION
            PENDING_ACTION = None
            if action["type"] == "call":
                result = run_api("termux-telephony-call", action["number"])
            else:
                result = run_api("termux-sms-send", "-n", action["number"], action["message"])
            say("action_done" if result and result.returncode == 0 else "action_error")
            return True
        if phrase in ("cancel", "no", "नहीं", "कैंसल", "रद्द"):
            PENDING_ACTION = None
            say("action_cancelled")
            return True
        PENDING_ACTION = None
        say("action_cancelled")
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
    elif phrase in ("contacts", "show contacts", "कॉन्टैक्ट्स दिखाओ"):
        list_contacts()
    elif phrase.startswith(("find contact ", "contact ", "कॉन्टैक्ट खोजो ")):
        query = re.sub(r"^(find contact|contact|कॉन्टैक्ट खोजो)\s+", "", phrase).strip()
        list_contacts(query)
    elif phrase.startswith(("call ", "कॉल ")):
        number = re.sub(r"^(call|कॉल)\s+", "", phrase).strip()
        if re.fullmatch(r"[+0-9][0-9 -]{5,18}", number):
            PENDING_ACTION = {"type":"call","number":re.sub(r"[^+0-9]","",number)}
            say("call_confirm", number=PENDING_ACTION["number"])
        else:
            say("call_usage")
    elif phrase.startswith(("sms ", "message ", "एसएमएस ")):
        parts = phrase.split(maxsplit=2)
        if len(parts) == 3 and re.fullmatch(r"[+0-9][0-9 -]{5,18}", parts[1]):
            PENDING_ACTION = {"type":"sms","number":re.sub(r"[^+0-9]","",parts[1]),"message":parts[2]}
            say("sms_confirm", number=PENDING_ACTION["number"], message=parts[2])
        else:
            say("sms_usage")
    elif phrase in ("camera", "open camera", "start camera", "कैमरा", "कैमरा खोलो", "फोटो खींचो", "लाइव कैमरा"):
        if companion_command("camera"):
            say("action_done")
        else:
            say("action_error")
    elif phrase.startswith(("open app ", "launch ", "ऐप खोलो ")) or (phrase.startswith("open ") and not phrase.startswith(("open settings ", "open youtuber ", "open streamer ", "open live stream "))):
        app = re.sub(r"^(open app|open|launch|ऐप खोलो)\s+", "", phrase).strip()
        launch_app(app)
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
    elif phrase in ("volume up", "increase volume", "आवाज बढ़ाओ", "वॉल्यूम बढ़ाओ", "आवाज तेज करो"):
        ok, level = change_volume(1)
        say("volume_set", stream="music", level=level) if ok else say("action_error")
    elif phrase in ("volume down", "decrease volume", "आवाज कम करो", "वॉल्यूम कम करो"):
        ok, level = change_volume(-1)
        say("volume_set", stream="music", level=level) if ok else say("action_error")
    elif phrase.startswith(("volume ", "वॉल्यूम ")):
        parts = phrase.split()
        try:
            stream = parts[1] if len(parts) > 2 else "music"
            level = int(parts[-1].replace("%", ""))
            result = set_volume(stream, level)
            ok, actual = result if isinstance(result, tuple) else (result, None)
            say("volume_set", stream=stream, level=actual) if ok else say("volume_usage")
        except (ValueError, IndexError):
            say("volume_usage")
    elif phrase.startswith(("brightness ", "ब्राइटनेस ")):
        value = phrase.split()[-1]
        try:
            level = int(value)
            if not 0 <= level <= 255:
                raise ValueError
            result = run_api("termux-brightness", str(level))
            say("brightness_set", level=level) if result and result.returncode == 0 else say("action_error")
        except ValueError:
            say("brightness_usage")
    elif phrase in ("play some song love", "play love song", "play a love song", "play romantic song", "play some romantic music", "love song", "कोई लव सॉन्ग चलाओ", "लव सॉन्ग चलाओ", "रोमांटिक गाना चलाओ", "कोई रोमांटिक गाना चलाओ", "प्यार वाला गाना चलाओ", "लव वाला गाना चलाओ"):
        say("love_song") if play_random_love_song() else say("action_error")
    elif phrase in ("pause music", "music pause", "म्यूजिक पॉज", "गाना रोक दो"):
        result = run_api("termux-media-player", "pause")
        say("media_done" if result and result.returncode == 0 else "media_error")
    elif phrase in ("resume music", "music resume", "म्यूजिक चालू", "गाना चालू करो"):
        result = run_api("termux-media-player", "resume")
        say("media_done" if result and result.returncode == 0 else "media_error")
    elif phrase in ("stop music", "music stop", "म्यूजिक बंद", "गाना बंद करो"):
        result = run_api("termux-media-player", "stop")
        say("media_done" if result and result.returncode == 0 else "media_error")
    elif phrase.startswith(("play music ", "play song ", "गाना चलाओ ")):
        filename = re.sub(r"^(play music|play song|गाना चलाओ)\s+", "", phrase).strip()
        say("media_started") if play_music(filename) else say("media_error")
    elif phrase.startswith(("notify ", "notification ", "नोटिफिकेशन ")):
        message = re.sub(r"^(notify|notification|नोटिफिकेशन)\s+", "", phrase).strip()
        say("notification_done") if send_notification(message) else say("action_error")
    elif phrase.startswith(("open settings ", "settings ", "सेटिंग खोलो ")):
        setting = re.sub(r"^(open settings|settings|सेटिंग खोलो)\s+", "", phrase).strip()
        setting = {"वाईफाई":"wifi", "वाइफाई":"wifi", "ब्लूटूथ":"bluetooth", "डिस्प्ले":"display", "साउंड":"sound", "ऐप":"apps", "सिक्योरिटी":"security", "वॉइस":"speech", "स्पीच":"speech"}.get(setting, setting)
        say("settings_open", setting=setting) if open_settings_page(setting) else say("settings_error")
    elif phrase in ("stopwatch start", "start stopwatch", "स्टॉपवॉच शुरू", "स्टॉपवॉच स्टार्ट"):
        global STOPWATCH_START
        STOPWATCH_START = time.monotonic()
        say("stopwatch_started")
    elif phrase in ("stopwatch stop", "stop stopwatch", "स्टॉपवॉच बंद", "स्टॉपवॉच रोकें"):
        if STOPWATCH_START is None:
            say("stopwatch_idle")
        else:
            elapsed = round(time.monotonic() - STOPWATCH_START, 2)
            STOPWATCH_START = None
            say("stopwatch_result", seconds=elapsed)
    elif phrase.startswith(("random ", "random number ", "रैंडम ")):
        parts = phrase.split()
        try:
            low, high = int(parts[-2]), int(parts[-1])
            if low > high or high - low > 1000000000:
                raise ValueError
            say("random_result", number=random.randint(low, high))
        except (ValueError, IndexError):
            say("unknown")
    elif phrase.startswith(("remind ", "reminder ", "रिमाइंड ")):
        match = re.match(r"^(?:remind|reminder|रिमाइंड)\s+(\d{1,4})\s+(.+)$", phrase)
        if match and 0 < int(match.group(1)) <= 1440:
            minutes, message = int(match.group(1)), match.group(2).strip()
            start_timer(minutes, message)
        else:
            say("timer_usage")
    elif phrase in ("wifi", "wifi status", "वाईफाई", "वाईफाई स्टेटस"):
        result = run_api("termux-wifi-connectioninfo")
        try:
            info = json.loads(result.stdout) if result and result.returncode == 0 else {}
            if info:
                safe_info = {k: info.get(k) for k in ("ssid", "ip", "link_speed_mbps", "frequency_mhz") if info.get(k) is not None}
                print("Wi-Fi:", json.dumps(safe_info, ensure_ascii=False))
            else:
                say("wifi_error")
        except json.JSONDecodeError:
            say("wifi_error")
    elif phrase in ("bluetooth", "bluetooth status", "ब्लूटूथ", "ब्लूटूथ स्टेटस"):
        result = run_api("termux-bluetoothinfo")
        try:
            info = json.loads(result.stdout) if result and result.returncode == 0 else {}
            if info:
                print("Bluetooth:", json.dumps(info, ensure_ascii=False))
            else:
                say("bluetooth_error")
        except json.JSONDecodeError:
            say("bluetooth_error")
    elif phrase in ("battery details", "बैटरी डिटेल्स"):
        result = run_api("termux-battery-status")
        try:
            info = json.loads(result.stdout) if result and result.returncode == 0 else {}
            if info:
                say("battery_details")
                print(json.dumps(info, ensure_ascii=False, indent=2))
            else:
                say("battery_error")
        except json.JSONDecodeError:
            say("battery_error")
    elif phrase in ("flashlight on", "torch on", "टॉर्च चालू", "लाइट चालू"):
        result = run_api("termux-torch", "on")
        say("torch_on" if result and result.returncode == 0 else "torch_error")
    elif phrase in ("flashlight off", "torch off", "टॉर्च बंद", "लाइट बंद"):
        result = run_api("termux-torch", "off")
        say("torch_off" if result and result.returncode == 0 else "torch_error")
    elif phrase in ("vibrate", "वाइब्रेट", "कंपन"):
        result = run_api("termux-vibrate", "-d", "300")
        say("vibrate" if result and result.returncode == 0 else "vibrate_error")
    elif phrase.startswith(("search ", "सर्च ")):
        query = re.sub(r"^(search|सर्च)\s+", "", phrase).strip()
        if query:
            result = run_api("termux-open-url", "https://www.google.com/search?q=" + quote(query))
            say("search", query=query) if result and result.returncode == 0 else say("unknown")
        else:
            say("unknown")
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
    elif phrase in ("scroll down", "screen scroll down", "नीचे स्क्रॉल करो", "नीचे करो"):
        say("action_done" if companion_command("scroll_down") else "action_error")
    elif phrase in ("scroll up", "screen scroll up", "ऊपर स्क्रॉल करो", "ऊपर करो"):
        say("action_done" if companion_command("scroll_up") else "action_error")
    elif phrase in ("go back", "back", "go back youtube", "पीछे जाओ", "वापस जाओ"):
        say("action_done" if companion_command("back") else "action_error")
    elif phrase in ("like", "like video", "video like karo", "वीडियो लाइक करो", "लाइक करो"):
        say("action_done" if companion_command("like") else "action_error")
    elif phrase in ("open comments", "show comments", "कमेंट खोलो", "कमेंट्स खोलो"):
        say("action_done" if companion_command("open_comments") else "action_error")
    elif phrase.startswith(("type comment ", "कमेंट लिखो ")):
        comment = re.sub(r"^(type comment|कमेंट लिखो)\\s+", "", phrase).strip()
        say("action_done" if comment and companion_command("type_comment", comment) else "action_error")
    elif phrase in ("lock phone", "lock screen", "phone lock karo", "फोन लॉक करो", "स्क्रीन लॉक करो"):
        say("action_done" if companion_command("lock_screen") else "action_error")
    elif phrase.startswith(("open youtuber ", "open streamer ", "youtube search ", "search youtube ", "यूट्यूबर खोलो ", "यूट्यूब पर खोजो ")):
        query = re.sub(r"^(open youtuber|open streamer|youtube search|search youtube|यूट्यूबर खोलो|यूट्यूब पर खोजो)\s+", "", phrase).strip()
        say("youtube_search", query=query) if open_youtube_search(query) else say("action_error")
    elif phrase.startswith(("open live stream ", "live stream ", "लाइव स्ट्रीम खोलो ")):
        query = re.sub(r"^(open live stream|live stream|लाइव स्ट्रीम खोलो)\\s+", "", phrase).strip()
        say("youtube_search", query=query) if open_youtube_search(query, live=True) else say("action_error")
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
                    "termux-battery-status", "termux-open-url",
                    "termux-torch", "termux-vibrate", "termux-contact-list",
                    "termux-telephony-call", "termux-sms-send", "monkey",
                    "termux-wifi-connectioninfo", "termux-bluetoothinfo",
                    "termux-volume", "termux-brightness", "termux-media-player",
                    "termux-notification", "am"):
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
