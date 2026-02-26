import telebot
from telebot import types
import sqlite3

# Tokeningiz o'rnatilgan
TOKEN = '8615427119:AAEnQffiDdQ1NHRHa1e3GLDqDsZEBymy7jg'
bot = telebot.TeleBot(TOKEN)

# Ma'lumotlar bazasini sozlash
def init_db():
    conn = sqlite3.connect('eco_bot.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, name TEXT, points INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

# Foydalanuvchi ballini olish
def get_points(user_id):
    conn = sqlite3.connect('eco_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT points FROM users WHERE id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else 0

# Reytingni olish (TOP 10)
def get_top():
    conn = sqlite3.connect('eco_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, points FROM users WHERE points > 0 ORDER BY points DESC LIMIT 10")
    top = cursor.fetchall()
    conn.close()
    return top

@bot.message_handler(commands=['start'])
def start(message):
    init_db()
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("📝 Ro'yxatdan o'tish")
    markup.add("🗑 Axlat tashlash", "🎁 Sovg'alar")
    markup.add("⭐ Ballarim", "🏆 Reyting")
    markup.add("📜 Qoidalar", "ℹ️ Bot haqida")
    bot.send_message(message.chat.id, "Xush kelibsiz! Maqsadi tabiatni asrash bo'lgan loyiha botiga xush kelibsiz.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    msg = message.text
    user_id = message.from_user.id

    if "Axlat tashlash" in msg:
        bot.send_message(message.chat.id, "Iltimos, rasm yuboring! 📸 Adminlar tekshirib ball berishadi.")
    
    elif "Ballarim" in msg:
        p = get_points(user_id)
        bot.send_message(message.chat.id, f"Sizning hozirgi ballingiz: {p} ball. ⭐")
    
    elif "Reyting" in msg:
        top_list = get_top()
        if not top_list:
            bot.send_message(message.chat.id, "🏆 Reyting hali shakllanmadi (ball olganlar yo'q).")
        else:
            text = "🏆 TOP Foydalanuvchilar:\n\n"
            for i, (name, pts) in enumerate(top_list, 1):
                text += f"{i}. {name} — {pts} ball\n"
            bot.send_message(message.chat.id, text)

    elif "Sovg'alar" in msg:
        bot.send_message(message.chat.id, "🎁 Sovg'alar:\n• 30 ball — Ruchka\n• 50 ball — Daftar\n• 75 ball — Kitob")
    
    elif "Qoidalar" in msg:
        bot.send_message(message.chat.id, "📜 Qoida: Rasmni aniq oling va admin javobini kuting.")

    elif "Ro'yxatdan o'tish" in msg:
        m = bot.send_message(message.chat.id, "Ism va familiyangizni yuboring:")
        bot.register_next_step_handler(m, save_user)

def save_user(message):
    conn = sqlite3.connect('eco_bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (id, name, points) VALUES (?, ?, ?)", 
                   (message.from_user.id, message.text, get_points(message.from_user.id)))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"Rahmat, {message.text}! Ro'yxatga olindi.")

if __name__ == "__main__":
    init_db()
    bot.infinity_polling()

