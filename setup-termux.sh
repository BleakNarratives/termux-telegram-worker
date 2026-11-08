#!/data/data/com.termux/files/usr/bin/bash
set -eu
pkg update -y
pkg install -y python git
python -m pip install --user -r requirements.txt
printf '\nInstalled dependencies. Run ./run.sh after exporting TG_TOKEN, TG_WEBHOOK_SECRET, and OLLAMA_MODEL.\n'
