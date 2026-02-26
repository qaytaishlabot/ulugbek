import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# 1. SOZLAMALAR
TOKEN = '8615427119:AAEnQffiDdQ1NHRHa1e3GLDqDsZEBymy7jg'
ADMIN_ID = 7543961611 
bot = telebot.TeleBot(TOKEN)

# 2. RENDER PORTINI OCHISH (Web Service uchun shart)
app = Flask('')

@app.route('/')
def home():
    return "Bot yoniq!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 3. RO'YXATDAN O'TISH VA BOT FUNKSIYALARI
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("📝 Ro'yxatdan o'tish", "🗑 Axlat tashlash", "🎁 Sovg'alar", "ℹ️ Bot haqida")
    bot.send_message(message.chat.id, "Xush kelibsiz! Avval ro'yxatdan o'ting.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📝 Ro'yxatdan o'tish")
def register(message):
    msg = bot.send_message(message.chat.id, "Ism va familiyangizni kiriting:")
    bot.register_next_step_handler(msg, save_user_info)

def save_user_info(message):
    info = (f"🆕 YANGI FOYDALANUVCHI:\n\n"
            f"👤 Ism: {message.text}\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"🔗 Username: @{message.from_user.username if message.from_user.username else 'yoq'}")
    
    # Sizga xabar yuboradi
    bot.send_message(ADMIN_ID, info)
    bot.send_message(message.chat.id, "✅ Rahmat! Ro'yxatdan o'tdingiz.")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if "Axlat tashlash" in message.text:
        bot.send_message(message.chat.id, "📸 Axlat rasmini yuboring.")
    elif "Sovg'alar" in message.text:
        bot.send_message(message.chat.id, "🎁 Yaqin kunlarda sovg'alar qo'shiladi!")
    else:
        bot.send_message(message.chat.id, "Tugmalardan foydalaning.")

# 4. ISHGA TUSHIRISH (Ikkita pastki chiziqqa diqqat qiling!)
if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    print("Bot polling boshlandi...")
    bot.infinity_polling()
