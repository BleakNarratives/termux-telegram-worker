#!/usr/bin/env python3
"""Minimal Telegram webhook that forwards private text prompts to local Ollama."""
import hmac
import os

import requests
from flask import Flask, abort, jsonify, request

app = Flask(__name__)
TOKEN = os.environ.get("TG_TOKEN", "")
MODEL = os.environ.get("OLLAMA_MODEL", "")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
WEBHOOK_SECRET = os.environ.get("TG_WEBHOOK_SECRET", "")


def answer(prompt: str) -> str:
    if not MODEL:
        return "Worker is not configured: set OLLAMA_MODEL to an installed model name."
    r = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": MODEL, "prompt": prompt, "stream": False},
        timeout=180,
    )
    r.raise_for_status()
    return r.json().get("response", "(No response from model)")[:4000]


def send_message(chat_id, text: str) -> None:
    if not TOKEN:
        raise RuntimeError("TG_TOKEN is not set")
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text[:4000]},
        timeout=30,
    )
    r.raise_for_status()


@app.get("/health")
def health():
    return jsonify(ok=True, service="termux-telegram-worker")


@app.post("/webhook")
def webhook():
    if WEBHOOK_SECRET:
        received = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if not hmac.compare_digest(received, WEBHOOK_SECRET):
            abort(403)
    update = request.get_json(silent=True) or {}
    message = update.get("message") or update.get("edited_message") or {}
    text = (message.get("text") or "").strip()
    chat_id = (message.get("chat") or {}).get("id")
    if not text or chat_id is None:
        return jsonify(ok=True, ignored=True)
    if text.startswith("/start"):
        reply = "Send a text prompt and I will pass it to the configured local model."
    else:
        try:
            reply = answer(text)
        except requests.RequestException:
            app.logger.exception("Ollama request failed")
            reply = "The local model is unavailable right now. Check Ollama and try again."
    try:
        send_message(chat_id, reply)
    except (requests.RequestException, RuntimeError):
        app.logger.exception("Telegram reply failed")
        return jsonify(ok=False, error="telegram-send-failed"), 502
    return jsonify(ok=True)


if __name__ == "__main__":
    # Local-only binding; expose it only through a tunnel you control.
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "8000")), debug=False)
