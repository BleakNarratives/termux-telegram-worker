#!/data/data/com.termux/files/usr/bin/bash
set -eu
cd "$(dirname "$0")"
: "${TG_TOKEN:?Set TG_TOKEN first}"
: "${TG_WEBHOOK_SECRET:?Set TG_WEBHOOK_SECRET first}"
: "${OLLAMA_MODEL:?Set OLLAMA_MODEL to an installed Ollama model}"
exec python app.py
