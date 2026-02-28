import telebot
from telebot import types
import os
import threading
from flask import Flask
import time
from datetime import date
import random  # AI / CV imitatsiyasi uchun

# --- 1. SOZLAMALAR ---
API_TOKEN = '8615427119:AAGlCJrpNusimALpU2GaZ304x6UvjniPLgo'
ADMIN_ID = 7543961611

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- Foydalanuvchilar va limit bazasi ---
users_data = {}
daily_limits = {}  # {user_id: {"date": "2026-02-28", "used": 0}}
MAX_DAILY = 3  # Kunlik limit

# --- Sovg'alar bazasi ---
GIFTS = {
    "ruchka": {"name": "🖋 Ruchka", "price": 30},
    "daftar": {"name": "📖 Daftar", "price": 50},
    "kitob":  {"name": "📚 Kitob", "price": 80}
}

@app.route('/')
def home():
    return "Bot tirik!"

# --- MENU TUGMALARI ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🎁 Sovg'alar", "💰 Mening ballarim")
    markup.row("📸 Rasm yuborish")
    markup.row("ℹ️ Bot haqida", "📜 Qoidalar")
    return markup

def registration_button():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("📝 Ro'yxatdan o'tish")
    return markup

# --- 2. Ro'yxatdan o'tish ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id not in users_data or not users_data[user_id].get('registered'):
        bot.send_message(message.chat.id, "Xush kelibsiz! Botdan foydalanish uchun ro'yxatdan o'ting:", reply_markup=registration_button())
    else:
        bot.send_message(message.chat.id, "Asosiy menyu:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "📝 Ro'yxatdan o'tish")
def ask_name(message):
    bot.send_message(message.chat.id, "Ism va familiyangizni kiriting:")
    bot.register_next_step_handler(message, process_registration)

def process_registration(message):
    user_id = message.from_user.id
    full_name = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Tasdiqlash ✅", callback_data=f"reg_ok_{user_id}_{full_name}"),
        types.InlineKeyboardButton("Rad etish ❌", callback_data=f"reg_no_{user_id}")
    )
    bot.send_message(ADMIN_ID, f"🆕 Ro'yxatdan o'tish:\n👤 {full_name}\n🆔 {user_id}", reply_markup=markup)
    bot.send_message(message.chat.id, "Ma'lumotlaringiz yuborildi. Admin tasdiqlashini kuting.")

# --- 3. Axlat turini aniqlash (imitatsiya AI) ---
def detect_trash_type(photo_file_id):
    """
    Boshlanishda tasodifiy tekshiruv:
    - 'plastic', 'paper', 'other'
    Keyinchalik real AI/CV model bilan almashtirish mumkin
    """
    choice = random.choices(['plastic', 'paper', 'other'], weights=[3,3,2])[0]
    return choice

# --- 4. Rasm qabul qilish ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    if user_id not in users_data or not users_data[user_id].get('registered'):
        bot.send_message(message.chat.id, "Avval ro'yxatdan o'ting!")
        return

    # Kunlik limit
    today = str(date.today())
    if user_id not in daily_limits or daily_limits[user_id]['date'] != today:
        daily_limits[user_id] = {"date": today, "used": 0}

    if daily_limits[user_id]['used'] >= MAX_DAILY:
        bot.send_message(message.chat.id, f"Bugun kunlik limit tugadi ({MAX_DAILY} rasm). Ertaga yana urinib ko'ring.")
        return

    # Axlat turini aniqlash
    trash_type = detect_trash_type(message.photo[-1].file_id)
    if trash_type == 'plastic':
        points = 2
        type_name = "Plastik (baklashka)"
    elif trash_type == 'paper':
        points = 2
        type_name = "Qog‘oz"
    else:
        points = 1
        type_name = "Oddiy musr / boshqa"

    # Ball berish
    users_data[user_id]['bal'] += points
    daily_limits[user_id]['used'] += 1

    bot.send_message(
        message.chat.id,
        f"Rasmingiz tasdiqlandi! ✅\nTur: {type_name}\n+{points} ball\nBugungi limit: {daily_limits[user_id]['used']}/{MAX_DAILY}"
    )

# --- 5. Matnli tugmalar ---
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = message.from_user.id
    if user_id not in users_data or not users_data[user_id].get('registered'):
        bot.send_message(message.chat.id, "Iltimos, avval ro'yxatdan o'ting.", reply_markup=registration_button())
        return

    if message.text == "💰 Mening ballarim":
        bot.send_message(message.chat.id, f"👤 {users_data[user_id]['name']}\n🪙 Ballaringiz: {users_data[user_id]['bal']}")
    elif message.text == "📜 Qoidalar":
        bot.send_message(message.chat.id, "Sifatli rasm yuboring va ball to'plang! Kunlik limit: 3 rasm.")
    elif message.text == "ℹ️ Bot haqida":
        bot.send_message(message.chat.id, "Bu rasm yuborib ball yig'ish botidir. Rasm avtomatik tekshiriladi.")
    elif message.text == "🎁 Sovg'alar":
        markup = types.InlineKeyboardMarkup()
        for key, item in GIFTS.items():
            markup.add(types.InlineKeyboardButton(f"{item['name']} - {item['price']} ball", callback_data=f"buy_{key}"))
        bot.send_message(
            message.chat.id,
            f"Balingiz: {users_data[user_id]['bal']}\nSovg'ani tanlang:",
            reply_markup=markup
        )

# --- 6. Callback query (Admin va sotib olish) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_all(call):
    data = call.data
    if data.startswith('reg_ok_'):
        u_id = int(data.split('_')[2])
        f_name = data.split('_')[3]
        users_data[u_id] = {'registered': True, 'bal': 0, 'name': f_name}
        bot.send_message(u_id, f"Tabriklaymiz {f_name}, tasdiqlandingiz!", reply_markup=main_menu())
        bot.edit_message_text(f"✅ {f_name} tasdiqlandi.", ADMIN_ID, call.message.message_id)
    elif data.startswith('buy_'):
        gift_key = data.split('_')[1]
        gift = GIFTS[gift_key]
        u_id = call.from_user.id
        if users_data[u_id]['bal'] >= gift['price']:
            users_data[u_id]['bal'] -= gift['price']
            bot.send_message(u_id, f"🎉 {gift['name']} sotib olindi!")
            bot.send_message(ADMIN_ID, f"🔔 Xarid: {users_data[u_id]['name']} - {gift['name']}")
        else:
            bot.answer_callback_query(call.id, "Ball yetarli emas!", show_alert=True)

# --- 7. Ishga tushirish ---
def run_bot():
    while True:
        try:
            bot.remove_webhook()
            bot.polling(none_stop=True, interval=0, timeout=20)
        except:
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
