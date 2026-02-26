
import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# 1. SOZLAMALAR
TOKEN = '8615427119:AAF44PaCDQCHIMHfzOGkx_QMGJCAaxrUBGA'
ADMIN_ID = 7543961611 
bot = telebot.TeleBot(TOKEN)

# 2. RENDER UCHUN WEB SERVER
app = Flask('')
@app.route('/')
def home(): return "Bot is live!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 3. KLAVIATURALAR (Tugmalar to'plami)
def start_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton("📝 Ro'yxatdan o'tish"))
    return markup

def main_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🗑 Axlat tashlash")
    btn2 = types.KeyboardButton("🎁 Sovg'alar")
    btn3 = types.KeyboardButton("📜 Qoidalar")
    btn4 = types.KeyboardButton("ℹ️ Bot haqida")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

# 4. BOT MANTIQI
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id, 
        "Xush kelibsiz! Botdan foydalanish uchun avval ro'yxatdan o'ting 👇", 
        reply_markup=start_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == "📝 Ro'yxatdan o'tish")
def register(message):
    msg = bot.send_message(message.chat.id, "Ism va familiyangizni kiriting:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, save_user_info)

def save_user_info(message):
    # Adminga ma'lumot yuborish
    info = (f"🆕 YANGI RO'YXATDAN O'TISH:\n\n"
            f"👤 Ism: {message.text}\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"🔗 Username: @{message.from_user.username if message.from_user.username else 'yoq'}")
    
    bot.send_message(ADMIN_ID, info)
    
    # Ro'yxatdan o'tgandan keyin ASOSIY MENYUga o'tkazish
    bot.send_message(
        message.chat.id, 
        "✅ Rahmat! Siz muvaffaqiyatli ro'yxatdan o'tdingiz. Endi xizmatlardan foydalanishingiz mumkin:", 
        reply_markup=main_menu_keyboard()
    )

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if message.text == "🗑 Axlat tashlash":
        bot.send_message(message.chat.id, "📸 Marhamat, axlat rasmini yuboring. Adminlar uni tekshirib ball berishadi.")
    
    elif message.text == "🎁 Sovg'alar":
        bot.send_message(message.chat.id, "🎁 Hozircha sovg'alar mavjud emas. Ball to'plashda davom eting!")
        
    elif message.text == "📜 Qoidalar":
        bot.send_message(message.chat.id, "📜 Qoidalar oddiy: \n1. Axlatni rasmga oling. \n2. Uni to'g'ri joyga tashlang. \n3. Ball oling!")
        
    elif message.text == "ℹ️ Bot haqida":
        bot.send_message(message.chat.id, "🌿 Ushbu bot tabiatni tozalashga hissa qo'shish uchun yaratilgan.\nAsoschi: Z.Ulugbek")
    
    else:
        bot.send_message(message.chat.id, "Iltimos, menyudagi tugmalardan birini tanlang.", reply_markup=main_menu_keyboard())

# 5. ISHGA TUSHIRISH
if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    bot.infinity_polling()
