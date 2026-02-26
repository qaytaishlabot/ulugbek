import telebot
from telebot import types
import sqlite3

TOKEN = '8615427119:AAG3rXwxXTGqvhVBzV-VSrHQllpco3CMqaQ'
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 12345678  # BU YERGA O'ZINGIZNING TELEGRAM ID-INGIZNI YOZING

# --- MA'LUMOTLAR BAZASI BILAN ISHLASH ---
def init_db():
    conn = sqlite3.connect('eco_bot.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, name TEXT, points INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def add_user(user_id, name):
    conn = sqlite3.connect('eco_bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (id, name, points) VALUES (?, ?, 0)", (user_id, name))
    conn.commit()
    conn.close()

def get_user_points(user_id):
    conn = sqlite3.connect('eco_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT points FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def get_top_users():
    conn = sqlite3.connect('eco_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, points FROM users ORDER BY points DESC LIMIT 10")
    top = cursor.fetchall()
    conn.close()
    return top

# --- BOT INTERFEYSI ---
@bot.message_handler(commands=['start'])
def start(message):
    init_db()
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("📝 Ro'yxatdan o'tish", "🗑 Axlat tashlash", "🎁 Sovg'alar", "⭐ Ballarim", "📜 Qoidalar", "🏆 Reyting")
    bot.send_message(message.chat.id, "Professional Eco-Botga xush kelibsiz!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    text = message.text
    user_id = message.from_user.id

    if "Ro'yxatdan o'tish" in text:
        msg = bot.send_message(message.chat.id, "Ismingizni kiriting:")
        bot.register_next_step_handler(msg, process_registration)

    elif "Axlat tashlash" in text:
        bot.send_message(message.chat.id, "Rasm yuboring, adminlar tekshirib ball berishadi! 📸")

    elif "Ballarim" in text:
        points = get_user_points(user_id)
        bot.send_message(message.chat.id, f"Sizning joriy ballingiz: {points} ⭐")

    elif "Reyting" in text:
        top = get_top_users()
        if not top:
            bot.send_message(message.chat.id, "Reyting hali shakllanmadi.")
        else:
            res = "🏆 TOP-10 Foydalanuvchilar:\n\n"
            for i, (name, pts) in enumerate(top, 1):
                res += f"{i}. {name} — {pts} ball\n"
            bot.send_message(message.chat.id, res)

    elif "Sovg'alar" in text:
        bot.send_message(message.chat.id, "🎁 Sovg'alar:\n- 30 ball: Ruchka\n- 50 ball: Daftar\n- 75 ball: Kitob")

def process_registration(message):
    add_user(message.from_user.id, message.text)
    bot.send_message(message.chat.id, f"Rahmat, {message.text}! Siz ro'yxatdan o'tdingiz.")

# Botni yurgizish
if __name__ == "__main__":
    init_db()
    bot.infinity_polling()
