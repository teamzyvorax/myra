# MYRA — ZYVORA Phone Voice Assistant

A free, Termux-first Android voice assistant starter. It uses Termux:API and the Android speech/TTS engines already available on the phone. No Google API key, paid API, or cloud account is required for the basic features.

## Features
- Speech input with `termux-speech-to-text`
- Spoken replies with `termux-tts-speak`
- Male-style / female-style voice presets (pitch/rate presets; the actual voice depends on the Android TTS engine installed on the phone)
- Hindi/English language preference
- Safe built-in commands: time, battery, open YouTube, open browser, help
- Typed-input fallback if Termux:API is unavailable
- No arbitrary shell-command execution

## Install on Android
1. Install **Termux** and **Termux:API** from the same trusted source (F-Droid is recommended). Do not mix Termux builds from different sources.
2. In Termux run:

```bash
pkg update -y && pkg upgrade -y
pkg install python termux-api git -y
git clone https://github.com/teamzyvorax/myra.git
cd myra
python main.py
```

3. Allow microphone permission when Android asks.

## Voice settings
Choose Male-style or Female-style in the assistant menu. These are pitch/rate presets, not guaranteed gender-specific voices. For genuinely different male and female voices, install/select two suitable voices in Android Settings → Text-to-speech output. Availability is device and language dependent.

## Commands
- `help` — show commands
- `time` — speak current time
- `battery` — read battery status (requires Termux:API)
- `youtube` — open YouTube
- `browser` — open a web search
- `voice` — switch voice preset
- `language` — switch Hindi/English
- `exit` — quit

## Privacy
Speech recognition may use the speech service configured on Android and may require internet depending on the installed recognizer. TTS is handled by the Android TTS engine. This project does not include analytics or transmit assistant chat history to a server.
