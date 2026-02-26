import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# 1. SOZLAMALAR
TOKEN = '8615427119:AAEnQffiDdQ1NHRHa1e3GLDqDsZEBymy7jg'
ADMIN_ID = 7543961611  # Sizning ID raqamingiz joylandi
bot = telebot.TeleBot(TOKEN)

# 2. RENDER UCHUN FLASK (Web Service bepul rejasi uchun shart)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running live!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 3. BOT FUNKSIYALARI
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("📝 Ro'yxatdan o'tish")
    btn2 = types.KeyboardButton("🗑 Axlat tashlash")
    btn3 = types.KeyboardButton("🎁 Sovg'alar")
    btn4 = types.KeyboardButton("ℹ️ Bot haqida")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, "Xush kelibsiz! Botdan foydalanish uchun ro'yxatdan o'ting.", reply_markup=markup)

# Ro'yxatdan o'tish jarayoni
@bot.message_handler(func=lambda message: message.text == "📝 Ro'yxatdan o'tish")
def register(message):
    msg = bot.send_message(message.chat.id, "Ism va familiyangizni yuboring:")
    bot.register_next_step_handler(msg, save_user_info)

def save_user_info(message):
    user_info = (
        f"🆕 **YANGI FOYDALANUVCHI:**\n\n"
        f"👤 Ism: {message.text}\n"
        f"🆔 ID: {message.from_user.id}\n"
        f"🔗 Username: @{message.from_user.username if message.from_user.username else 'Mavjud emas'}"
    )
    
    # Ma'lumotni SIZGA (Adminga) yuboradi
    bot.send_message(ADMIN_ID, user_info, parse_mode="Markdown")
    
    # Foydalanuvchiga tasdiq xabari
    bot.send_message(message.chat.id, "✅ Rahmat! Ma'lumotlaringiz adminlarga yuborildi.")

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    if "Axlat tashlash" in message.text:
        bot.send_message(message.chat.id, "📸 Iltimos, axlat rasmini yuboring. Adminlar ko'rib chiqishadi.")
    elif "Sovg'alar" in message.text:
        bot.send_message(message.chat.id, "🎁 Sovg'alar ro'yxati yaqin kunlarda e'lon qilinadi!")
    elif "Bot haqida" in message.text:
        bot.send_message(message.chat.id, "🌿 Bu bot tabiatni asrash uchun yaratildi.\nAsoschi: Z.Ulugbek")
    else:
        bot.send_message(message.chat.id, "Iltimos, menyudagi tugmalardan foydalaning.")

# 4. ISHGA TUSHIRISH (Xatosiz formatda)
if name == "__main__":
    # Flaskni alohida oqimda yurgizamiz
    t = Thread(target=run_flask)
    t.start()
    
    print("Bot polling boshlandi...")
    bot.infinity_polling()
