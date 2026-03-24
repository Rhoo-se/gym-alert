# Swim Seat Alert

Lightweight watcher for seat openings on the Seongnam Sports Complex course page.

## Setup

1) Create a Telegram bot with @BotFather.
2) Send any message to your bot once.
3) Get your `chat_id`:

```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

## Run

Create `.env` and fill in your values:

```
python3 /Users/rho/Desktop/Practice/PythonProject/swim_alert.py
```

Optional overrides:

```
POLL_SECONDS=60 TARGET_PGM_NM="..." python3 /Users/rho/Desktop/Practice/PythonProject/swim_alert.py
```

Notes:
- Default target is the class name the user provided.
- A notification is sent only when the class changes from full to available.
