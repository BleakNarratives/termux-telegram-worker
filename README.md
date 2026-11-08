# Termux Telegram → local Ollama worker

A small runnable webhook: Telegram text message → local Ollama → Telegram reply. No paid API, database, Docker, or GitHub Actions required.

## Install in Termux

```sh
pkg install -y git python
 git clone https://github.com/BleakNarratives/termux-telegram-worker.git
cd termux-telegram-worker
python -m pip install --user -r requirements.txt
```

Remove the leading space before `git clone` if your shell copied it oddly; the command is `git clone ...`.

Set the bot token from BotFather and the exact model name shown by `ollama list`:

```sh
export TG_TOKEN='your-bot-token'
export OLLAMA_MODEL='your-installed-model'
export TG_WEBHOOK_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
```

Ollama must already be running and reachable at `http://127.0.0.1:11434` (override with `OLLAMA_URL` if needed). Start the worker:

```sh
./run.sh
```

In another Termux session, verify the process:

```sh
curl -fsS http://127.0.0.1:8000/health
```

## Connect Telegram

The worker listens only on localhost. Use your existing HTTPS tunnel to forward to `http://127.0.0.1:8000`; then set its public base URL and register the webhook. These commands use the secret from the same shell where you started the worker:

```sh
export PUBLIC_BASE_URL='https://your-public-tunnel-host'
curl -fsS "https://api.telegram.org/bot${TG_TOKEN}/setWebhook" \
  -H 'Content-Type: application/json' \
  -d "$(python -c 'import json,os; print(json.dumps({"url":os.environ["PUBLIC_BASE_URL"].rstrip("/")+"/webhook","secret_token":os.environ["TG_WEBHOOK_SECRET"]}))')"
```

Telegram sends the secret in a request header; the app rejects webhook requests without the matching secret. Keep `TG_TOKEN` and `TG_WEBHOOK_SECRET` private. Do not commit them.

## Optional background run

Stop the foreground worker, then run:

```sh
mkdir -p "$HOME/.local/state/termux-telegram-worker"
nohup ./run.sh >> "$HOME/.local/state/termux-telegram-worker/worker.log" 2>&1 < /dev/null &
```

View its log:

```sh
tail -n 50 "$HOME/.local/state/termux-telegram-worker/worker.log"
```

## Configuration

- `TG_TOKEN` — Telegram bot token (required)
- `TG_WEBHOOK_SECRET` — webhook secret (required)
- `OLLAMA_MODEL` — installed Ollama model name (required)
- `OLLAMA_URL` — defaults to `http://127.0.0.1:11434`
- `PORT` — defaults to `8000`

This is a working message-processing loop, not an automatic income source. It only responds to people who message your bot.
