# MYRA — ZYVORA Phone Voice Assistant

A free, Termux-first Android voice assistant. Basic features use Android speech recognition, Android Text-to-Speech, and Termux:API. No paid API key is required.

## Features
- Voice input using `termux-speech-to-text`
- Spoken replies using `termux-tts-speak`
- Male-style and female-style pitch/rate presets
- Hindi and English response modes
- Time, battery, YouTube, browser, help, and exit commands
- Typed-input fallback
- System diagnostics with `python main.py --check`
- No arbitrary shell-command execution

## Quick install

Install Termux and Termux:API from the same trusted source. F-Droid is recommended; do not mix builds from different sources.

In Termux:

```bash
pkg update -y && pkg upgrade -y
pkg install python termux-api git -y
git clone https://github.com/teamzyvorax/myra.git
cd myra
python main.py
```

For an existing checkout:

```bash
cd ~/myra
git pull
python main.py
```

## Commands

| Say/type | Action |
|---|---|
| help / हेल्प | List commands |
| time / समय | Current time |
| battery / बैटरी | Battery percentage |
| youtube / यूट्यूब | Open YouTube |
| browser / गूगल | Open Google |
| male / मेल | Male-style preset |
| female / फीमेल | Female-style preset |
| hindi / हिंदी | Hindi replies |
| english | English replies |
| voice | Toggle voice preset |
| language | Toggle language |
| exit | Quit MYRA |

## Diagnostics

```bash
python main.py --check
```

Install the Android **Termux:API** companion app and grant microphone permission. Termux and Termux:API must come from the same distribution source.

## Voice notes

Male/female are pitch and rate presets, not guaranteed gender-specific voices. The actual voice depends on the voices installed in Android Settings → Text-to-speech output. Speech recognition can depend on the Android recognizer and may require internet depending on device settings.

## Privacy and safety

MYRA does not upload chat history to a MYRA server. Android's configured speech recognizer may process voice input according to that service's own privacy settings. MYRA does not execute arbitrary spoken shell commands.
