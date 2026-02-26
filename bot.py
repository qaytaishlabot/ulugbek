import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# 1. SOZLAMALAR
TOKEN = '8615427119:AAEnQffiDdQ1NHRHa1e3GLDqDsZEBymy7jg'
ADMIN_ID = 7543961611 
bot = telebot.TeleBot(TOKEN)

# 2. RENDER UCHUN WEB SERVER (O'chib qolmasligi uchun)
app = Flask('')

@app.route('/')
def home():
    return "Bot is live!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 3. BOT FUNKSIYALARI (Ro'yxatdan o'tish bilan)
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("📝 Ro'yxatdan o'tish")
    btn2 = types.KeyboardButton("🗑 Axlat tashlash")
    btn3 = types.KeyboardButton("🎁 Sovg'alar")
    btn4 = types.KeyboardButton("ℹ️ Bot haqida")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, "Xush kelibsiz! Botdan foydalanish uchun avval ro'yxatdan o'ting.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📝 Ro'yxatdan o'tish")
def register(message):
    msg = bot.send_message(message.chat.id, "Ism va familiyangizni kiriting:")
    bot.register_next_step_handler(msg, save_user_info)

def save_user_info(message):
    text = (f"🆕 YANGI RO'YXATDAN O'TISH:\n\n"
            f"👤 Ism: {message.text}\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"🔗 Username: @{message.from_user.username if message.from_user.username else 'Yoq'}")
    
    bot.send_message(ADMIN_ID, text) # Sizga xabar keladi
    bot.send_message(message.chat.id, "✅ Rahmat! Ma'lumotlaringiz adminlarga yuborildi.")

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if "Axlat tashlash" in message.text:
        bot.send_message(message.chat.id, "📸 Axlat rasmini yuboring.")
    else:
        bot.send_message(message.chat.id, "Iltimos, menyudan foydalaning.")

# 4. TO'G'RI ISHGA TUSHIRISH (Xato shu yerda edi)
if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    print("Bot ishga tushdi...")
    bot.infinity_polling()
