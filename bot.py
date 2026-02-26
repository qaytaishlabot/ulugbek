import telebot
from telebot import types
import os
import threading
from flask import Flask
import time

# --- 1. SOZLAMALAR ---
API_TOKEN = '8615427119:AAGlCJrpNusimALpU2GaZ304x6UvjniPLgo' 
ADMIN_ID = 7543961611 

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Foydalanuvchilar bazasi
users_data = {}

# Sovg'alar bazasi
GIFTS = {
    "ruchka": {"name": "🖋 Ruchka", "price": 30},
    "daftar": {"name": "📖 Daftar", "price": 50},
    "kitob":  {"name": "📚 Kitob", "price": 80}
}

# --- 2. WEBSERVER (RENDER UCHUN) ---
@app.route('/')
def home():
    return "Bot tirik!"

# --- 3. MENU TUGMALARI ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🎁 Sovg'alar", "💰 Mening ballarim")
    markup.row("📸 Rasm yuborish (2 ball)")
    markup.row("ℹ️ Bot haqida", "📜 Qoidalar")
    return markup

def registration_button():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("📝 Ro'yxatdan o'tish")
    return markup

# --- 4. BOT MANTIQI ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id not in users_data or not users_data[user_id].get('registered'):
        bot.send_message(message.chat.id, 
                         "Xush kelibsiz! Botdan foydalanish uchun avval ro'yxatdan o'tishingiz kerak. \nPastdagi tugmani bosing:", 
                         reply_markup=registration_button())
    else:
        name = users_data[user_id]['name']
        bot.send_message(message.chat.id, f"Salom {name}, xush kelibsiz!", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "📝 Ro'yxatdan o'tish")
def ask_name(message):
    bot.send_message(message.chat.id, "Ism va familiyangizni kiriting (Masalan: Ali Valiyev):")
    bot.register_next_step_handler(message, process_registration)

def process_registration(message):
    user_id = message.from_user.id
    full_name = message.text
    
    if len(full_name.split()) < 2:
        bot.send_message(message.chat.id, "Iltimos, ism VA familiyangizni to'liq kiriting:")
        bot.register_next_step_handler(message, process_registration)
        return

    # Adminga yuborish uchun tugmalar
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Tasdiqlash ✅", callback_data=f"reg_ok_{user_id}_{full_name}"),
               types.InlineKeyboardButton("Rad etish ❌", callback_data=f"reg_no_{user_id}"))
    
    bot.send_message(ADMIN_ID, f"🆕 Yangi foydalanuvchi:\n👤 Ism: {full_name}\n🆔 ID: {user_id}", reply_markup=markup)
    bot.send_message(message.chat.id, "Ma'lumotlaringiz adminga yuborildi. Tasdiqlashni kuting... ⏳")

# --- 5. TUGMALAR JAVOBI ---

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith('reg_ok_'):
        # Format: reg_ok_ID_FullName
        parts = call.data.split('_')
        u_id = int(parts[2])
        full_name = parts[3]
        
        users_data[u_id] = {'registered': True, 'bal': 0, 'name': full_name}
        bot.send_message(u_id, f"Tabriklaymiz {full_name}! Ro'yxatdan o'tdingiz va barcha bo'limlar ochildi. ✅", reply_markup=main_menu())
        bot.edit_message_text(f"✅ {full_name} tasdiqlandi.", ADMIN_ID, call.message.message_id)

    elif call.data.startswith('reg_no_'):
        u_id = int(call.data.split('_')[2])
        bot.send_message(u_id, "Afsuski, ro'yxatdan o'tish so'rovingiz rad etildi. ❌")
        bot.edit_message_text("❌ Ro'yxatdan o'tish rad etildi.", ADMIN_ID, call.message.message_id)

    # Ballar va sovg'alar logikasi (avvalgi koddagidek qoladi)
    elif call.data.startswith('accept_'):
        u_id = int(call.data.split('_')[1])
        users_data[u_id]['bal'] += 2
        bot.send_message(u_id, "Rasmingiz tasdiqlandi! +2 ball ✅")
        bot.edit_message_caption("Tasdiqlandi ✅", ADMIN_ID, call.message.message_id)

    elif call.data.startswith('buy_'):
        gift_key = call.data.split('_')[1]
        gift = GIFTS[gift_key]
        u_id = call.from_user.id
        if users_data[u_id]['bal'] >= gift['price']:
            users_data[u_id]['bal'] -= gift['price']
            bot.send_message(u_id, f"🎉 {gift['name']} sotib olindi!")
            bot.send_message(ADMIN_ID, f"🔔 XARID: {users_data[u_id]['name']} - {gift['name']}")
        else:
            bot.answer_callback_query(call.id, "Ball yetarli emas! ❌", show_alert=True)

# --- MATNLI TUGMALAR (About, Rules, Balance) ---
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    if user_id not in users_data or not users_data[user_id].get('registered'):
        bot.send_message(message.chat.id, "Avval ro'yxatdan o'ting!", reply_markup=registration_button())
        return

    if message.text == "💰 Mening ballarim":
        user = users_data[user_id]
        bot.send_message(message.chat.id, f"👤 {user['name']}\n🪙 Ballaringiz: {user['bal']}")
    elif message.text == "📜 Qoidalar":
        bot.send_message(message.chat.id, "1. Rasm yuboring.\n2. Ball yig'ing.\n3. Sovg'a oling.")
    elif message.text == "ℹ️ Bot haqida":
        bot.send_message(message.chat.id, "Bu ball yig'ish va sovg'alar olish botidir.")

# --- 6. ISHGA TUSHIRISH ---
def run_bot():
    while True:
        try:
            bot.remove_webhook()
            bot.polling(none_stop=True)
        except:
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
