import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# 1. BOT SOZLAMALARI
TOKEN = '8615427119:AAG3rXwxXTGqvhVBzV-VSrHQllpco3CMqaQ'
bot = telebot.TeleBot(TOKEN)

# 2. RENDER UCHUN PORT (HIYLA)
app = Flask('')

@app.route('/')
def home():
    return "Bot yoniq!"

def run_flask():
    # Render avtomatik port beradi, bo'lmasa 8080 ishlatamiz
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
    bot.send_message(message.chat.id, "Xush kelibsiz! Bot stabil rejimda ishlayapti.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    if "Axlat tashlash" in message.text:
        bot.send_message(message.chat.id, "📸 Rasm yuboring, adminlar tekshiradi.")
    elif "Sovg'alar" in message.text:
        bot.send_message(message.chat.id, "🎁 Sovg'alar: Ruchka, Daftar, Kitob.")
    else:
        bot.send_message(message.chat.id, "Iltimos, menyudan foydalaning.")

# 4. BOTNI VA FLASKNI BIRGA ISHLATISH
if __name__ == "__main__":
    # Flaskni alohida oqimda (thread) yurgizamiz
    t = Thread(target=run_flask)
    t.start()
    
    print("Bot ishga tushdi...")
    bot.infinity_polling()
