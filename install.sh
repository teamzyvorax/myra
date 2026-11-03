#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "== MYRA installer =="
if [ -z "${PREFIX:-}" ] || [ ! -d "$PREFIX" ]; then
  echo "Please run this installer inside Termux on Android."
  exit 1
fi

pkg update -y
pkg install -y python termux-api git

if [ ! -f main.py ]; then
  echo "main.py not found. Run this from the MYRA project folder."
  exit 1
fi

chmod +x main.py
echo
echo "MYRA setup complete."
echo "Start:   python main.py"
echo "Check:   python main.py --check"
echo
echo "Install the Termux:API Android app separately and grant microphone permission."
