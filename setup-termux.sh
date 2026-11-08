#!/usr/bin/env bash
set -eu
pkg update -y
pkg install -y python
python -m pip install --user -r requirements.txt
printf '\nInstalled. Set TG_TOKEN and OLLAMA_MODEL, then run: ./run.sh\n'
