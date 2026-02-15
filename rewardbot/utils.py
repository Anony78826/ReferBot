from config import SEPARATOR
from database import load_messages_text, load_used, save_used


def split_messages(raw_text):
    blocks = [x.strip() for x in raw_text.split(SEPARATOR)]
    blocks = [x for x in blocks if x.strip() != ""]
    return blocks


def get_available_messages():
    raw_text = load_messages_text()
    messages = split_messages(raw_text)

    used = load_used()
    available = []

    for i, msg in enumerate(messages):
        if i not in used:
            available.append((i, msg))

    return messages, used, available


def reserve_messages(count):
    messages, used, available = get_available_messages()

    if len(available) < count:
        return None

    selected = available[:count]  # take first available messages

    for idx, _ in selected:
        used.append(idx)

    save_used(used)

    return [msg for _, msg in selected]
    