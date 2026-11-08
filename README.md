# Termux helper: Telegram inbox -> local Ollama -> Telegram reply

This repo is a real, small worker—not a revenue promise. It accepts Telegram webhook updates, sends text to a local Ollama model, and replies in the same chat. It does not message strangers, scrape leads, or spend money.

## Install in Termux

```sh
pkg install -y python git
 git clone https://github.com/BleakNarratives/termux-telegram-worker.git
cd termux-telegram-worker
python -m pip install --user -r requirements.txt
```

Have Ollama running and a model available. Set the model name to one you already have (`ollama list`):

```sh
export OLLAMA_MODEL='your-installed-model'
export TG_TOKEN='your-BotFather-token'
```

Start the worker in the foreground first so errors are visible:

```sh
python app.py
```

In another Termux session, verify it:

```sh
curl -fsS http://127.0.0.1:8000/health
```

## Telegram webhook

The worker requires a public HTTPS URL forwarding to port 8000. Once you have that URL, register it (the token is read from the environment, not stored in the repository):

```sh
curl -fsS "https://api.telegram.org/bot${TG_TOKEN}/setWebhook" \
  -H 'Content-Type: application/json' \
  -d "$(python -c 'import json,os; print(json.dumps({"url":os.environ["PUBLIC_BASE_URL"].rstrip("/")+"/webhook"}))')"
```

Set `PUBLIC_BASE_URL` to the tunnel URL in the same shell before running that command. Keep the token private; do not commit it or paste it into a public issue.

## Optional background run

After foreground testing, use the included `run.sh`. It writes logs under `~/ .local/state/termux-telegram-worker` (with no space: `~/.local/state/termux-telegram-worker`):

```sh
mkdir -p "$HOME/.local/state/termux-telegram-worker"
nohup ./run.sh >> "$HOME/.local/state/termux-telegram-worker/worker.log" 2>&1 &
```

This worker only replies to Telegram updates. It cannot guarantee income; receiving paid work still depends on a real customer and an agreed service.
