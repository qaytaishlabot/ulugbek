import telebot
from telebot import types
import sqlite3

TOKEN = "8615427119:AAF44PaCDQCHIMHfzOGkx_QMGJCAaxrUBGA"
ADMIN_ID = 7543961611

bot = telebot.TeleBot(TOKEN)

# ================= DATABASE =================
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    points INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS photos (
    file_id TEXT PRIMARY KEY,
    user_id INTEGER,
    latitude REAL,
    longitude REAL,
    status TEXT
)
""")
conn.commit()

# ================= START =================
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 Ro'yxatdan o'tish")
    bot.send_message(message.chat.id,
                     "👋 Xush kelibsiz!\nRo'yxatdan o'ting.",
                     reply_markup=markup)

# ================= REGISTER =================
@bot.message_handler(func=lambda m: m.text == "📝 Ro'yxatdan o'tish")
def register(message):
    msg = bot.send_message(message.chat.id, "✍ Ism familiyangizni yozing:")
    bot.register_next_step_handler(msg, save_user)

def save_user(message):
    cursor.execute("INSERT OR REPLACE INTO users (user_id, name, points) VALUES (?, ?, COALESCE((SELECT points FROM users WHERE user_id=?),0))",
                   (message.from_user.id, message.text, message.from_user.id))
    conn.commit()

    bot.send_message(ADMIN_ID,
                     f"🆕 Yangi user\n👤 {message.text}\n🆔 {message.from_user.id}")

    main_menu(message.chat.id)

# ================= MENU =================
def main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🗑 Axlat tashlash")
    markup.row("🎁 Sovg'alar", "📜 Qoidalar")
    markup.row("ℹ Bot haqida")
    bot.send_message(chat_id, "📌 Asosiy menyu:", reply_markup=markup)

# ================= QOIDALAR =================
@bot.message_handler(func=lambda m: m.text == "📜 Qoidalar")
def rules(message):
    text = ("📜 QOIDALAR:\n\n"
            "1. Axlatni rasmga oling.\n"
            "2. Lokatsiyani yuboring.\n"
            "3. Tasdiqlansa 2 ball.\n"
            "4. Soxta rasm yubormang.")
    bot.send_message(message.chat.id, text)

# ================= BOT HAQIDA =================
@bot.message_handler(func=lambda m: m.text == "ℹ Bot haqida")
def about(message):
    text = ("🤖 Bizning botimizda axlatni rasmga olib pul ishlashingiz mumkin.\n\n"
            "📅 2026.02.26\n"
            "👑 Asoschi: Z.Ulugbek")
    bot.send_message(message.chat.id, text)

# ================= SOVGALAR =================
@bot.message_handler(func=lambda m: m.text == "🎁 Sovg'alar")
def gifts(message):
    cursor.execute("SELECT points FROM users WHERE user_id=?", (message.from_user.id,))
    result = cursor.fetchone()
    if not result:
        return

    points = result[0]

    text = (f"🎁 Sizning ballaringiz: {points}\n\n"
            "30 ball - ✏ Ruchka\n"
            "50 ball - 📒 Daftar\n"
            "80 ball - 📚 Kitob")
    bot.send_message(message.chat.id, text)

# ================= AXLAT TASHLASH =================
@bot.message_handler(func=lambda m: m.text == "🗑 Axlat tashlash")
def trash(message):
    bot.send_message(message.chat.id, "📸 Avval axlat rasmini yuboring.")

# ================= PHOTO =================
user_waiting_location = {}

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_id = message.photo[-1].file_id
    user_waiting_location[message.from_user.id] = file_id
    bot.send_message(message.chat.id, "📍 Endi lokatsiyani yuboring.")

# ================= LOCATION =================
@bot.message_handler(content_types=['location'])
def handle_location(message):
    user_id = message.from_user.id

    if user_id not in user_waiting_location:
        return

    file_id = user_waiting_location[user_id]
    latitude = message.location.latitude
    longitude = message.location.longitude

    cursor.execute("INSERT INTO photos VALUES (?, ?, ?, ?, ?)",
                   (file_id, user_id, latitude, longitude, "pending"))
    conn.commit()

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Tasdiqlash (2 ball)", callback_data=f"ok_{file_id}"),
        types.InlineKeyboardButton("❌ Rad etish", callback_data=f"no_{file_id}")
    )

    bot.send_photo(ADMIN_ID, file_id,
                   caption=f"📸 Yangi rasm\nUser: {user_id}\n📍 {latitude}, {longitude}",
                   reply_markup=markup)

    bot.send_message(user_id, "⏳ Rasm va lokatsiya adminga yuborildi.")

    del user_waiting_location[user_id]

# ================= ADMIN APPROVE =================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    data = call.data
    action, file_id = data.split("_")

    cursor.execute("SELECT user_id FROM photos WHERE file_id=?", (file_id,))
    result = cursor.fetchone()

    if not result:
        return

    user_id = result[0]

    if action == "ok":
        cursor.execute("UPDATE users SET points = points + 2 WHERE user_id=?", (user_id,))
        cursor.execute("UPDATE photos SET status='approved' WHERE file_id=?", (file_id,))
        conn.commit()

        bot.send_message(user_id, "🎉 Rasm tasdiqlandi! +2 ball")
        bot.answer_callback_query(call.id, "Ball berildi")

    elif action == "no":
        cursor.execute("UPDATE photos SET status='rejected' WHERE file_id=?", (file_id,))
        conn.commit()

        bot.send_message(user_id, "❌ Kechirasiz, rasmingiz tasdiqlanmadi.")
        bot.answer_callback_query(call.id, "Rad etildi")

bot.infinity_polling(skip_pending=True)
