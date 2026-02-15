import telebot
import os

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_TOKEN, CHANNEL_USERNAME, ADMIN_ID, REWARD_NEW_USER, REWARD_REFERRAL, SEPARATOR
from database import (
    ensure_files,
    load_users,
    save_users,
    load_pending,
    save_pending,
    load_messages_text,
    save_messages_text,
    load_used,
    save_used
)
from utils import reserve_messages, split_messages

bot = telebot.TeleBot(BOT_TOKEN)

os.makedirs("downloads", exist_ok=True)


def is_admin(user_id):
    return int(user_id) == int(ADMIN_ID)


def check_join(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        status = member.status
        if status in ["member", "administrator", "creator"]:
            return True
        return False
    except Exception as e:
        print(f"Error checking join status: {e}")
        return False


def register_user(user):
    users = load_users()
    uid = str(user.id)

    if uid not in users:
        users[uid] = {
            "username": user.username if user.username else "",
            "registered": False,
            "joined": False,
            "referrals": 0,
            "referred_by": None,
            "reward_taken": 0,
            "reward_history": []
        }

    save_users(users)


def set_registered(uid):
    users = load_users()
    uid = str(uid)

    if uid in users:
        users[uid]["registered"] = True
        save_users(users)


def set_joined(uid):
    users = load_users()
    uid = str(uid)

    if uid in users:
        users[uid]["joined"] = True
        save_users(users)


def add_rewards_count(uid, count, msgs):
    users = load_users()
    uid = str(uid)

    if uid in users:
        users[uid]["reward_taken"] += count
        if "reward_history" not in users[uid]:
            users[uid]["reward_history"] = []
        users[uid]["reward_history"].extend(msgs)
        # Keep only last 50 for history management, but user only sees 5
        users[uid]["reward_history"] = users[uid]["reward_history"][-50:]
        save_users(users)


def give_rewards(user_id, count):
    msgs = reserve_messages(count)
    if not msgs:
        bot.send_message(user_id, "❌ **ʀᴇᴡᴀʀᴅ ꜱᴛᴏᴄᴋ ꜰɪɴɪꜱʜᴇᴅ!** ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ.", parse_mode="Markdown")
        return False

    for m in msgs:
        bot.send_message(user_id, f"🎁 **ʀᴇᴡᴀʀᴅ ᴍᴇꜱꜱᴀɢᴇ:**\n\n`{m}`", parse_mode="Markdown")

    add_rewards_count(user_id, count, msgs)
    return True


def process_referral(new_user_id):
    pending = load_pending()
    uid = str(new_user_id)

    if uid not in pending:
        return

    referrer_id = pending[uid]

    if str(referrer_id) == str(new_user_id):
        del pending[uid]
        save_pending(pending)
        return

    users = load_users()

    if str(referrer_id) in users:
        users[str(referrer_id)]["referrals"] += 1
        save_users(users)

        bot.send_message(
            referrer_id, 
            "🎉 **ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ ʀᴇꜰᴇʀʀᴀʟ!**\nʏᴏᴜ ɢᴏᴛ 3 ᴇxᴛʀᴀ ʀᴇᴡᴀʀᴅ ᴍᴇꜱꜱᴀɢᴇꜱ!",
            parse_mode="Markdown"
        )
        give_rewards(referrer_id, REWARD_REFERRAL)

    del pending[uid]
    save_pending(pending)


def join_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}"))
    markup.add(InlineKeyboardButton("✅ ᴄʜᴇᴄᴋ ᴊᴏɪɴ", callback_data="check_join"))
    return markup


@bot.message_handler(commands=["start"])
def start_cmd(message):
    ensure_files()
    register_user(message.from_user)

    args = message.text.split()
    if len(args) > 1:
        ref_id = args[1]
        pending = load_pending()
        if str(message.from_user.id) not in pending:
            pending[str(message.from_user.id)] = ref_id
            save_pending(pending)

    if not check_join(message.from_user.id):
        welcome_text = (
            "👋 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ **ʀᴇᴡᴀʀᴅ ʙᴏᴛ**!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ɪɴ order ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ʙᴏᴛ ᴀɴᴅ ʀᴇᴄᴇɪᴠᴇ ʏᴏᴜʀ ʀᴇᴡᴀʀᴅꜱ, "
            "ʏᴏᴜ ᴍᴜꜱᴛ ʙᴇ ᴀ ᴍᴇᴍʙᴇʀ ᴏꜰ ᴏᴜʀ ᴏꜰꜰɪᴄɪᴀʟ ᴄʜᴀɴɴᴇʟ.\n\n"
            "ᴘʟᴇᴀꜱᴇ ᴊᴏɪɴ ʙᴇʟᴏᴡ ᴀɴᴅ ᴄʟɪᴄᴋ **ᴄʜᴇᴄᴋ ᴊᴏɪɴ**."
        )
        bot.send_message(message.chat.id, welcome_text, reply_markup=join_markup(), parse_mode="Markdown")
        return

    set_joined(message.from_user.id)
    users = load_users()
    uid = str(message.from_user.id)

    if not users[uid]["registered"]:
        bot.send_message(
            message.chat.id, 
            "✨ **ᴊᴏɪɴ ᴄᴏɴꜰɪʀᴍᴇᴅ!**\n\nʏᴏᴜ ᴀʀᴇ ᴀʟᴍᴏꜱᴛ ᴛʜᴇʀᴇ. ꜱᴇɴᴅ /register ᴛᴏ ᴄʟᴀɪᴍ ʏᴏᴜʀ ᴡᴇʟᴄᴏᴍᴇ ʀᴇᴡᴀʀᴅꜱ! 🎁",
            parse_mode="Markdown"
        )
    else:
        bot.send_message(
            message.chat.id, 
            "🌟 **ᴡᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ!**\n\nʏᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ᴀ ʀᴇɢɪꜱᴛᴇʀᴇᴅ ᴍᴇᴍʙᴇʀ.\n\n"
            "💡 ᴜꜱᴇ /reward ᴛᴏ ᴠɪᴇᴡ ʏᴏᴜʀ ɢɪꜰᴛꜱ ᴏʀ /ref ᴛᴏ ɪɴᴠɪᴛᴇ ꜰʀɪᴇɴᴅꜱ.",
            parse_mode="Markdown"
        )


@bot.message_handler(commands=["register"])
def register_cmd(message):
    if not check_join(message.from_user.id):
        bot.send_message(message.chat.id, "⚠️ **ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ!**\n\nᴘʟᴇᴀꜱᴇ ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ꜰɪʀꜱᴛ.", reply_markup=join_markup(), parse_mode="Markdown")
        return

    users = load_users()
    uid = str(message.from_user.id)

    if uid not in users:
        register_user(message.from_user)
        users = load_users()

    if users[uid]["registered"]:
        bot.send_message(message.chat.id, "✅ **ʏᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ʀᴇɢɪꜱᴛᴇʀᴇᴅ.**", parse_mode="Markdown")
        return

    users[uid]["registered"] = True
    users[uid]["joined"] = True
    save_users(users)

    bot.send_message(
        message.chat.id, 
        "🎊 **ʀᴇɢɪꜱᴛʀᴀᴛɪᴏɴ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ!**\n\n"
        "ʏᴏᴜ ʜᴀᴠᴇ ᴇᴀʀɴᴇᴅ **2 ʀᴇᴡᴀʀᴅ ᴍᴇꜱꜱᴀɢᴇꜱ**. ꜱᴇɴᴅɪɴɢ ᴛʜᴇᴍ ɴᴏᴡ... 📥",
        parse_mode="Markdown"
    )

    ok = give_rewards(message.from_user.id, REWARD_NEW_USER)
    if ok:
        process_referral(message.from_user.id)


@bot.message_handler(commands=["reward"])
def reward_cmd(message):
    if not check_join(message.from_user.id):
        bot.send_message(message.chat.id, "⚠️ ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ꜰɪʀꜱᴛ!", reply_markup=join_markup(), parse_mode="Markdown")
        return

    users = load_users()
    uid = str(message.from_user.id)

    if uid not in users or not users[uid]["registered"]:
        bot.send_message(message.chat.id, "❌ **ᴘʟᴇᴀꜱᴇ ʀᴇɢɪꜱᴛᴇʀ ꜰɪʀꜱᴛ ᴜꜱɪɴɢ /register**", parse_mode="Markdown")
        return

    history = users[uid].get("reward_history", [])
    if not history:
        bot.send_message(message.chat.id, "🎁 **ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ ʀᴇᴄᴇɪᴠᴇᴅ ᴀɴʏ ʀᴇᴡᴀʀᴅꜱ ʏᴇᴛ.**", parse_mode="Markdown")
        return

    last_5 = history[-5:]
    text = "💎 **ʏᴏᴜʀ ʟᴀꜱᴛ 5 ʀᴇᴡᴀʀᴅꜱ:**\n\n"
    for i, msg in enumerate(reversed(last_5), 1):
        text += f"🔹 `{msg}`\n━━━━━━━━━━━━━━━━\n"

    file_name = f"{bot.get_me().username}.txt"
    file_path = os.path.join("downloads", f"{uid}_{file_name}")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"--- REWARD HISTORY FOR @{users[uid]['username']} ---\n\n")
        for i, msg in enumerate(history, 1):
            f.write(f"[{i}] {msg}\n{'-'*30}\n")

    with open(file_path, "rb") as f:
        bot.send_document(message.chat.id, f, caption=text, visible_file_name=file_name, parse_mode="Markdown")


@bot.message_handler(commands=["cmds"])
def cmds_cmd(message):
    bot.send_message(
        message.chat.id,
        "🛠 **ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅꜱ**\n\n"
        "🔹 /start - `ɪɴɪᴛɪᴀʟɪᴢᴇ ʙᴏᴛ`\n"
        "🔹 /register - `ᴄʟᴀɪᴍ ᴊᴏɪɴɪɴɢ ʙᴏɴᴜꜱ`\n"
        "🔹 /reward - `ᴠɪᴇᴡ ʏᴏᴜʀ ʀᴇᴡᴀʀᴅꜱ`\n"
        "🔹 /ref - `ɢᴇᴛ ʀᴇꜰᴇʀʀᴀʟ ʟɪɴᴋ`\n"
        "🔹 /cmds - `ꜱʜᴏᴡ ᴛʜɪꜱ ʟɪꜱᴛ`\n"
        "🔹 /admin - `ᴄᴏɴᴛʀᴏʟ ᴘᴀɴᴇʟ` (ᴀᴅᴍɪɴꜱ ᴏɴʟʏ)",
        parse_mode="Markdown"
    )


@bot.message_handler(commands=["ref"])
def referral_cmd(message):
    if not check_join(message.from_user.id):
        bot.send_message(message.chat.id, "⚠️ ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ꜰɪʀꜱᴛ!", reply_markup=join_markup(), parse_mode="Markdown")
        return

    users = load_users()
    uid = str(message.from_user.id)

    if uid not in users or not users[uid]["registered"]:
        bot.send_message(message.chat.id, "❌ **ᴘʟᴇᴀꜱᴇ ʀᴇɢɪꜱᴛᴇʀ ꜰɪʀꜱᴛ.**", parse_mode="Markdown")
        return

    ref_count = users[uid].get("referrals", 0)
    link = f"https://t.me/{bot.get_me().username}?start={uid}"
    bot.send_message(
        message.chat.id,
        f"📊 **ʀᴇꜰᴇʀʀᴀʟ ᴅᴀsʜʙᴏᴀʀᴅ**\n\n"
        f"✅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ ʀᴇꜰᴇʀʀᴀʟꜱ: `{ref_count}`\n\n"
        f"🔗 **ʏᴏᴜʀ ᴜɴɪQᴜᴇ ʟɪɴᴋ:**\n`{link}`\n\n"
        f"💡 *ɪɴᴠɪᴛᴇ ꜰʀɪᴇɴᴅꜱ ᴛᴏ ᴇᴀʀɴ 3 ʀᴇᴡᴀʀᴅꜱ ᴘᴇʀ referral!*",
        parse_mode="Markdown"
    )


# ================= ADMIN COMMANDS ===================

@bot.message_handler(commands=["admin"])
def admin_cmd(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ This command is only for admins.")
        return

    bot.send_message(
        message.chat.id,
        "👑 Admin Panel Commands:\n\n"
        "/addtxt - Upload new txt messages file\n"
        "/users - Total registered users\n"
        "/stock - Show total/used/remaining messages\n"
        "/resetused - Reset used messages (allow reuse)\n"
        "/broadcast - Send message to all users\n"
    )


@bot.message_handler(commands=["users"])
def users_cmd(message):
    if not is_admin(message.from_user.id):
        return

    users = load_users()
    bot.send_message(message.chat.id, f"👥 Total Users: {len(users)}")


@bot.message_handler(commands=["stock"])
def stock_cmd(message):
    if not is_admin(message.from_user.id):
        return

    raw = load_messages_text()
    messages = split_messages(raw)

    used = load_used()
    total = len(messages)
    used_count = len(used)
    remaining = total - used_count

    bot.send_message(
        message.chat.id,
        f"📦 Stock Info:\n\n"
        f"Total Messages: {total}\n"
        f"Used Messages: {used_count}\n"
        f"Remaining Messages: {remaining}"
    )


@bot.message_handler(commands=["resetused"])
def reset_used_cmd(message):
    if not is_admin(message.from_user.id):
        return

    save_used([])
    bot.send_message(message.chat.id, "✅ Used message list reset. Messages can be reused now.")


@bot.message_handler(commands=["addtxt"])
def addtxt_cmd(message):
    if not is_admin(message.from_user.id):
        return

    bot.send_message(message.chat.id, "📤 Send your .txt file now (messages separated by ---)")


@bot.message_handler(content_types=["document"])
def handle_document(message):
    if not is_admin(message.from_user.id):
        return

    file_name = message.document.file_name

    if not file_name.endswith(".txt"):
        bot.send_message(message.chat.id, "❌ Only .txt file allowed.")
        return

    file_info = bot.get_file(message.document.file_id)
    if file_info.file_path is None:
        bot.send_message(message.chat.id, "❌ Error retrieving file path.")
        return
    downloaded_file = bot.download_file(file_info.file_path)

    save_path = os.path.join("downloads", file_name)

    with open(save_path, "wb") as f:
        f.write(downloaded_file)

    with open(save_path, "r", encoding="utf-8") as f:
        new_text = f.read()

    old_text = load_messages_text()

    if old_text.strip() == "":
        final_text = new_text
    else:
        final_text = old_text.strip() + "\n" + SEPARATOR + "\n" + new_text.strip()

    save_messages_text(final_text)

    bot.send_message(message.chat.id, f"✅ File added successfully: {file_name}")


@bot.message_handler(commands=["broadcast"])
def broadcast_cmd(message):
    if not is_admin(message.from_user.id):
        return

    msg = bot.send_message(message.chat.id, "📢 Please send the message you want to broadcast (or type /cancel):")
    bot.register_next_step_handler(msg, process_broadcast_text)


def process_broadcast_text(message):
    if message.text == "/cancel":
        bot.send_message(message.chat.id, "❌ Broadcast cancelled.")
        return

    users = load_users()
    sent = 0
    failed = 0

    status_msg = bot.send_message(message.chat.id, "⏳ Sending broadcast...")

    for uid in users:
        try:
            if message.content_type == 'text':
                bot.send_message(uid, f"📢 Broadcast:\n\n{message.text}")
            elif message.content_type == 'photo':
                bot.send_photo(uid, message.photo[-1].file_id, caption=message.caption)
            else:
                bot.copy_message(uid, message.chat.id, message.message_id)
            sent += 1
        except Exception:
            failed += 1

    bot.edit_message_text(f"✅ Broadcast Done\nSent: {sent}\nFailed: {failed}", message.chat.id, status_msg.message_id)


@bot.message_handler(func=lambda m: m.text and m.text.startswith("/broadcast "))
def broadcast_send_fallback(message):
    if not is_admin(message.from_user.id):
        return

    text = message.text.replace("/broadcast ", "", 1)
    if not text:
        bot.send_message(message.chat.id, "❌ Please provide text for broadcast.")
        return

    users = load_users()
    sent = 0
    failed = 0

    status_msg = bot.send_message(message.chat.id, "⏳ Sending broadcast...")

    for uid in users:
        try:
            bot.send_message(uid, f"📢 Broadcast:\n\n{text}")
            sent += 1
        except:
            failed += 1

    bot.edit_message_text(f"✅ Broadcast Done\nSent: {sent}\nFailed: {failed}", message.chat.id, status_msg.message_id)


print("🤖 Bot is running...")
ensure_files()
bot.infinity_polling()
