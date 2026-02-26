import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# 1. TOKENINGIZNI SHU YERGA TO'G'RI QO'YING
TOKEN = '8615427119:AAEnQffiDdQ1NHRHa1e3GLDqDsZEBymy7jg'
bot = telebot.TeleBot(TOKEN)

# 2. RENDER UCHUN FLASK (PORT BINDING)
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 3. BOT FUNKSIYALARI
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🗑 Axlat tashlash")
    btn2 = types.KeyboardButton("🎁 Sovg'alar")
    btn3 = types.KeyboardButton("📜 Qoidalar")
    btn4 = types.KeyboardButton("ℹ️ Bot haqida")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, "Xush kelibsiz! Bot hozir ishlayapti.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    if "Axlat tashlash" in message.text:
        bot.send_message(message.chat.id, "📸 Iltimos, rasm yuboring.")
    else:
        bot.send_message(message.chat.id, "Pastdagi menyudan foydalaning.")

# 4. ISHGA TUSHIRISH
if name == "__main__":
    # Flaskni alohida oqimda yurgizamiz
    t = Thread(target=run_flask)
    t.start()
    
    print("Bot polling boshlandi...")
    bot.infinity_polling()
