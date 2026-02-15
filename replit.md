# Replit Agent Guide

## Overview

This is a Telegram reward/referral bot built in Python. The bot incentivizes users to join a Telegram channel and refer others. Users earn rewards in the form of messages/content that are distributed from a pre-loaded pool. The bot tracks user registrations, channel join status, referrals, and distributes unique messages as rewards.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **Framework**: pyTelegramBotAPI (telebot) v4.16.1
- **Why**: Lightweight, synchronous Telegram bot library for Python. Simple to use for a single-purpose bot like this.
- **Entry point**: `rewardbot/main.py` (the actual bot logic; `main.py` at root is a placeholder)

### Data Storage
- **Approach**: File-based JSON and plain text storage in the `data/` directory
- **No database server** is used — all persistence is through flat files
- **Files**:
  - `data/users.json` — User registry keyed by Telegram user ID. Each user has: username, registered status, joined status, referral count, who referred them, and rewards taken count.
  - `data/used.json` — Array of indices tracking which messages from the pool have already been distributed as rewards.
  - `data/pending_ref.json` — Tracks pending referral relationships (before a referred user completes required actions).
  - `data/messages.txt` — Pool of reward messages/content separated by `"---"` delimiter. Admin uploads content here.
  - `data/message.txt` — Appears unused currently; may be legacy or placeholder.

### Reward System
- **New user reward**: 2 messages (`REWARD_NEW_USER = 2`)
- **Referral reward**: 3 messages (`REWARD_REFERRAL = 3`)
- Messages are consumed sequentially from `messages.txt` and tracked by index in `used.json` to prevent duplicates.
- `utils.py` handles splitting the message pool by the separator and reserving available (unused) messages.

### User Flow
1. User starts bot (possibly via referral link)
2. Bot checks if user has joined the required Telegram channel (`@IG_CC_SELLERS`)
3. User must join channel and click "Check Join" button to verify
4. Upon verification, user is registered and receives reward messages
5. Referrer gets additional reward messages when their referral completes the flow

### Configuration
- All config lives in `rewardbot/config.py`: bot token, channel username, admin ID, reward amounts, and message separator
- **Note**: The bot token is hardcoded in config.py. This should ideally be moved to environment variables for security.

### Project Structure
```
├── main.py                  # Root placeholder (not the bot)
├── data/                    # Persistent storage directory
│   ├── users.json           # User data
│   ├── used.json            # Consumed message indices
│   ├── pending_ref.json     # Pending referrals
│   ├── messages.txt         # Reward message pool
│   └── message.txt          # Unused/legacy
├── rewardbot/
│   ├── main.py              # Bot entry point and handlers
│   ├── config.py            # Bot configuration constants
│   ├── database.py          # File I/O helpers for JSON/text storage
│   ├── utils.py             # Message splitting and reservation logic
│   └── requirements.txt     # Python dependencies
```

### Key Design Decisions
- **File-based storage vs database**: Chose flat files for simplicity. Works fine for small-scale use but would need migration to a proper database (SQLite, PostgreSQL) for concurrent access or larger user bases. Race conditions are possible with multiple simultaneous file writes.
- **Sequential message distribution**: Messages are given out in order (first available), not randomly. This is simple and predictable.
- **Incomplete code**: `database.py` is truncated (missing `load_used` and other functions). The bot's `main.py` handler registrations are also incomplete. These need to be finished.

## External Dependencies

### Third-Party Services
- **Telegram Bot API** — Core dependency. The bot communicates via Telegram's Bot API using the pyTelegramBotAPI library. Requires a valid bot token from BotFather.
- **Telegram Channel** (`@IG_CC_SELLERS`) — Users must join this channel to receive rewards. The bot checks membership status via the API.

### Python Packages
- `pyTelegramBotAPI==4.16.1` — Telegram bot framework
- `requests` — HTTP library (likely used for any direct API calls)

### Environment Requirements
- Python 3.x
- Bot must be added as an administrator to the target Telegram channel to check member status
- The bot token in `config.py` should be migrated to an environment variable (e.g., `BOT_TOKEN` env var)