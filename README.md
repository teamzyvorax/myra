# MYRA — ZYVORA Phone Voice Assistant

A free, Termux-first Android voice assistant using Android speech recognition, Android Text-to-Speech, and Termux:API. No paid API key is required for the built-in features.

## Features
- Voice input and spoken replies
- Hindi and English response modes
- Male-style and female-style pitch/rate presets
- Current time and date
- Battery status
- Open YouTube and Google in the phone browser
- Save notes and list the latest 20 notes
- Basic safe calculator (arithmetic only; no Python code execution)
- Countdown timers with spoken completion alert while MYRA remains running
- Typed-input fallback and system diagnostics
- No arbitrary shell-command execution

## Install

Install Termux and the Termux:API Android app from the same trusted source (F-Droid is recommended). In Termux:

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
python main.py --check
python main.py
```

## Commands

| Say or type | Action |
|---|---|
| help / हेल्प | List commands |
| time / समय | Current time |
| date / तारीख | Current date |
| battery / बैटरी | Battery percentage |
| youtube / यूट्यूब | Open YouTube |
| browser / गूगल | Open Google |
| male / मेल | Male-style voice preset |
| female / फीमेल | Female-style voice preset |
| hindi / हिंदी | Hindi replies |
| english | English replies |
| note buy milk | Save a note |
| show notes / नोट्स दिखाओ | List saved notes |
| calculate 12 * 8 | Calculate arithmetic |
| timer 5 | Start a 5-minute countdown |
| exit | Quit MYRA |

## Important notes
- Male/female are pitch/rate presets, not guaranteed gender-specific voices. Actual voice depends on Android's installed TTS voices.
- Speech recognition may need internet depending on the Android recognizer selected on the phone.
- Countdown timers alert only while MYRA's Python process is running; they are not Android system alarms.
- Notes are stored locally in `notes.json` in the project folder.
- Install the Termux:API Android companion app and grant microphone permission.
- MYRA does not send chat history to a MYRA server and does not execute arbitrary spoken shell commands.
