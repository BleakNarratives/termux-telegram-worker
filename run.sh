#!/data/data/com.termux/files/usr/bin/bash
set -eu
cd "$(dirname "$0")"
: "${TG_TOKEN:?Set TG_TOKEN in your shell first}"
: "${OLLAMA_MODEL:?Set OLLAMA_MODEL to a model already installed in Ollama}"
exec python app.py
