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

@app.route('/')
def home():
    return "Bot tirik!"

# --- 2. MENU TUGMALARI ---
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

# --- 3. BOT MANTIQI ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id not in users_data or not users_data[user_id].get('registered'):
        bot.send_message(message.chat.id, "Xush kelibsiz! Botdan foydalanish uchun avval ro'yxatdan o'ting:", reply_markup=registration_button())
    else:
        bot.send_message(message.chat.id, "Asosiy menyu:", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "📝 Ro'yxatdan o'tish")
def ask_name(message):
    bot.send_message(message.chat.id, "Ism va familiyangizni kiriting:")
    bot.register_next_step_handler(message, process_registration)

def process_registration(message):
    user_id = message.from_user.id
    full_name = message.text
    # Adminga tasdiqlash uchun yuborish
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Tasdiqlash ✅", callback_data=f"reg_ok_{user_id}_{full_name}"),
               types.InlineKeyboardButton("Rad etish ❌", callback_data=f"reg_no_{user_id}"))
    bot.send_message(ADMIN_ID, f"🆕 Ro'yxatdan o'tish:\n👤 {full_name}\n🆔 {user_id}", reply_markup=markup)
    bot.send_message(message.chat.id, "Ma'lumotlaringiz yuborildi. Admin tasdiqlashini kuting.")

# --- Rasm qabul qilish ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    if user_id not in users_data or not users_data[user_id].get('registered'):
        bot.send_message(message.chat.id, "Avval ro'yxatdan o'ting!")
        return

    name = users_data[user_id].get('name', 'Noma\'lum')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Tasdiqlash ✅", callback_data=f"pic_ok_{user_id}"),
               types.InlineKeyboardButton("Rad etish ❌", callback_data=f"pic_no_{user_id}"))
    
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, 
                   caption=f"📸 Rasm: {name}\n🆔 {user_id}", reply_markup=markup)
    bot.send_message(message.chat.id, "Rasm adminga yuborildi. Yana rasm yuborishingiz yoki boshqa tugmani bosishingiz mumkin.")

# --- Matnli tugmalar ---
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    if user_id not in users_data or not users_data[user_id].get('registered'):
        bot.send_message(message.chat.id, "Iltimos, avval ro'yxatdan o'ting.", reply_markup=registration_button())
        return

    if message.text == "💰 Mening ballarim":
        bot.send_message(message.chat.id, f"👤 {users_data[user_id]['name']}\n🪙 Ballaringiz: {users_data[user_id]['bal']}")
    elif message.text == "📜 Qoidalar":
        bot.send_message(message.chat.id, "Sifatli rasm yuboring va ball to'plang!")
    elif message.text == "ℹ️ Bot haqida":
        bot.send_message(message.chat.id, "Bu rasm yuborib ball yig'ish botidir.")
    elif message.text == "🎁 Sovg'alar":
        markup = types.InlineKeyboardMarkup()
        for key, item in GIFTS.items():
            markup.add(types.InlineKeyboardButton(f"{item['name']} - {item['price']} ball", callback_data=f"buy_{key}"))
        bot.send_message(message.chat.id, f"Balingiz: {users_data[user_id]['bal']}\nSovg'ani tanlang:", reply_markup=markup)

# --- Callback query (Admin va Sotib olish) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_all(call):
    data = call.data
    if data.startswith('reg_ok_'):
        u_id = int(data.split('_')[2])
        f_name = data.split('_')[3]
        users_data[u_id] = {'registered': True, 'bal': 0, 'name': f_name}
        bot.send_message(u_id, f"Tabriklaymiz {f_name}, tasdiqlandingiz!", reply_markup=main_menu())
        bot.edit_message_text(f"✅ {f_name} tasdiqlandi.", ADMIN_ID, call.message.message_id)
    
    elif data.startswith('pic_ok_'):
        u_id = int(data.split('_')[2])
        users_data[u_id]['bal'] += 2
        bot.send_message(u_id, "Rasmingiz tasdiqlandi! +2 ball ✅")
        bot.edit_message_caption("✅ Tasdiqlandi", ADMIN_ID, call.message.message_id)

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

# --- ISHGA TUSHIRISH ---
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
