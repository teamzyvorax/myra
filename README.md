# MYRA — ZYVORA Phone Voice Assistant

A free, Termux-first Android voice assistant using Android speech recognition, Android Text-to-Speech, and Termux:API. No paid API key is required for the built-in features.

## Features
- Voice input and spoken replies
- Hindi and English response modes
- Male-style and female-style pitch/rate presets
- Current time and date
- Battery status
- Flashlight on/off (requires Termux:API and device support)
- Phone vibration (requires Termux:API)
- Media volume control (music/ring/alarm/notification/system/call streams where Android permits)
- Screen brightness control (0–255; device and Android policy dependent)
- Music playback/pause/resume/stop for audio files in Termux shared Music storage
- Android notifications from spoken messages
- Shortcuts to Wi-Fi, Bluetooth, display, sound, app and security settings
- Google web search by voice or typed command
- Safe app launcher for WhatsApp, Chrome, YouTube, Settings, Maps and Gmail
- Contact lookup by name (requires contacts permission)
- Wi-Fi connection details (SSID/IP when Android exposes them)
- Bluetooth status details
- Detailed battery status (health, temperature and charging fields when available)
- Phone calls and SMS only after a spoken/typed confirmation
- Open YouTube and Google in the phone browser
- Save notes and list the latest 20 notes
- Basic safe calculator (arithmetic only; no Python code execution)
- Countdown timers and custom spoken reminders while MYRA remains running
- Stopwatch with start/stop commands
- Random number generator with a user-defined range
- Typed-input fallback and system diagnostics
- No arbitrary shell-command execution

## Install

Install Termux and the Termux:API Android app from the same trusted source (F-Droid is recommended). In Termux:

```bash
pkg update -y && pkg upgrade -y
pkg install python termux-api git -y
git clone https://github.com/teamzyvorax/myra.git
cd myra
termux-setup-storage
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
| flashlight on / टॉर्च चालू | Turn phone flashlight on |
| flashlight off / टॉर्च बंद | Turn phone flashlight off |
| vibrate / वाइब्रेट | Vibrate phone briefly |
| search cats / सर्च cats | Search Google for words |
| open app whatsapp | Launch an allowlisted app |
| contacts | List saved contacts and numbers |
| find contact sam | Find a contact by name |
| call 9876543210 | Ask confirmation before calling |
| sms 9876543210 hello | Ask confirmation before sending SMS |
| wifi / wifi status | Show available Wi-Fi connection details |
| bluetooth / bluetooth status | Show Bluetooth status details |
| battery details | Show detailed battery status |
| volume up / volume down | Raise or lower music volume |
| volume music 70 | Set music volume to about 70% (device maximum is detected when available) |
| brightness 120 | Set screen brightness (0–255) |
| play music song.mp3 | Play a file from shared Music storage |
| pause music / resume music / stop music | Control MYRA's media player |
| notify Meeting starts in 5 minutes | Post an Android notification |
| open settings wifi | Open Android Wi-Fi settings |
| open settings bluetooth | Open Android Bluetooth settings |
| open settings display / sound / apps / security / speech | Open the matching Android settings page |
| confirm / हाँ | Confirm a pending call or SMS |
| cancel / नहीं | Cancel a pending call or SMS |
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
| remind 5 drink water | Speak a reminder after 5 minutes |
| random 1 100 | Generate a random number from 1 to 100 |
| stopwatch start / stopwatch stop | Measure elapsed time |
| exit | Quit MYRA |

## Important notes
- Male/female are pitch/rate presets, not guaranteed gender-specific voices. Actual voice depends on Android's installed TTS voices.
- Speech recognition may need internet depending on the Android recognizer selected on the phone. For Hindi recognition, set Hindi as the preferred language in Android's speech/voice input settings (MYRA can open this with `open settings speech`). Hindi spoken replies are selected with `hindi`.
- Timers and reminders alert only while MYRA's Python process is running; they are not Android system alarms and will not survive closing MYRA or rebooting the phone.
- The stopwatch runs only while MYRA is open; it is not a background service.
- Notes are stored locally in `notes.json` in the project folder.
- Install the Termux:API Android companion app from the same source as Termux. Grant only the Android permissions for features you actually use.
- Run `termux-setup-storage` to let MYRA access the shared Music folder. Music playback is restricted to audio files inside shared Music storage or the MYRA project folder.
- Android may block direct changes to Wi-Fi/Bluetooth radios and some system settings. MYRA opens the relevant Settings page instead of bypassing Android restrictions.
- Brightness, volume, media, notifications and app launching depend on Android version, device manufacturer, Termux:API version and granted permissions.
- Calls and SMS are never initiated until you explicitly say/type `confirm`; `cancel` discards the pending action.
- App launching is restricted to MYRA's built-in allowlist; arbitrary package or shell commands are not accepted.
- MYRA does not send chat history to a MYRA server and does not execute arbitrary spoken shell commands.
