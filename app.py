#!/usr/bin/env python3
"""Telegram webhook that forwards text prompts to a local Ollama instance."""
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
        return "Worker configuration error: OLLAMA_MODEL is not set."
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": MODEL, "prompt": prompt, "stream": False},
        timeout=180,
    )
    response.raise_for_status()
    return (response.json().get("response") or "(No response from model)")[:4000]


def send_message(chat_id, text: str) -> None:
    response = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text[:4000]},
        timeout=30,
    )
    response.raise_for_status()


@app.get("/health")
def health():
    return jsonify(ok=True, service="termux-telegram-worker")


@app.post("/webhook")
def webhook():
    if not TOKEN or not WEBHOOK_SECRET:
        app.logger.error("TG_TOKEN and TG_WEBHOOK_SECRET must be set")
        return jsonify(ok=False, error="worker-not-configured"), 503

    received_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if not hmac.compare_digest(received_secret, WEBHOOK_SECRET):
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
            reply = "The local model is unavailable. Check Ollama and try again."

    try:
        send_message(chat_id, reply)
    except requests.RequestException:
        app.logger.exception("Telegram reply failed")
        return jsonify(ok=False, error="telegram-send-failed"), 502
    return jsonify(ok=True)


if __name__ == "__main__":
    if not TOKEN or not WEBHOOK_SECRET:
        raise SystemExit("Set TG_TOKEN and TG_WEBHOOK_SECRET before starting.")
    # Bind locally; let the user's chosen tunnel expose it.
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "8000")), debug=False)
