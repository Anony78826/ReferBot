import json
import os

DATA_DIR = "data"

USERS_FILE = os.path.join(DATA_DIR, "users.json")
USED_FILE = os.path.join(DATA_DIR, "used.json")
PENDING_FILE = os.path.join(DATA_DIR, "pending_ref.json")
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.txt")


def ensure_files():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)

    if not os.path.exists(USED_FILE):
        with open(USED_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)

    if not os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)

    if not os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
            f.write("")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_users():
    return load_json(USERS_FILE)


def save_users(users):
    save_json(USERS_FILE, users)


def load_used():
    return load_json(USED_FILE)


def save_used(used):
    save_json(USED_FILE, used)


def load_pending():
    return load_json(PENDING_FILE)


def save_pending(pending):
    save_json(PENDING_FILE, pending)


def load_messages_text():
    with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
        return f.read()


def save_messages_text(text):
    with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
        f.write(text)
        