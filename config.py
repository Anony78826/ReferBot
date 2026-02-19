import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "8581545651:AAFZVVNNqs2ug8MMLwhI5hgXc3irfP04VKo")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@Xm_Checker")
ADMIN_ID = int(os.getenv("ADMIN_ID", 1295478989))

REWARD_NEW_USER = int(os.getenv("REWARD_NEW_USER", 2))
REWARD_REFERRAL = int(os.getenv("REWARD_REFERRAL", 3))

SEPARATOR = os.getenv("SEPARATOR", "---")