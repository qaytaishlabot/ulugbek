import telebot
from telebot import types
import threading
from flask import Flask
import os
import time

# --- SOZLAMALAR ---
API_TOKEN = '8615427119:AAGlCJrpNusimALpU2GaZ304x6UvjniPLgo'  # Oxirgi yangi tokeningiz
ADMIN_ID = 7543961611 
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Foydalanuvchi ma'lumotlari (Eslatma: Bot o'chsa, bu ma'lumotlar o'chadi)
# Doimiy saqlash uchun kelajakda Database qo'shish kerak
users_data = {}

# Sovg'alar ro'yxati
GIFTS = {
    "ruchka": {"name": "🖋 Ruchka", "price": 30},
    "daftar": {"name": "📖 Daftar", "price": 50},
    "kitob":  {"name": "📚 Kitob", "price": 80}
}

@app.route('/')
def home():
    return "Bot is running!"

def get_user(user_id):
    if user_id not in users_data:
        users_data[user_id] = {'registered': False, 'bal': 0, 'name': ''}
    return users_data[user_id]

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🎁 Sovg'alar", "💰 Mening ballarim")
    markup.row("📸 Rasm yuborish (2 ball)")
    return markup

# --- BOT LOGIKASI ---

@bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.from_user.id)
    if not user['registered']:
        bot.send_message(message.chat.id, "Xush kelibsiz! Botdan foydalanish uchun ismingizni yozing:")
        bot.register_next_step_handler(message, register_user)
    else:
        bot.send_message(message.chat.id, f"Salom, {user['name']}! Kerakli bo'limni tanlang:", reply_markup=main_menu())

def register_user(message):
    user_id = message.from_user.id
    name = message.text
    users_data[user_id]['name'] = name
    users_data[user_id]['registered'] = True
    bot.send_message(message.chat.id, f"Rahmat, {name}! Ro'yxatdan o'tdingiz.", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "💰 Mening ballarim")
def my_balance(message):
    user = get_user(message.from_user.id)
    bot.send_message(message.chat.id, f"👤 Ism: {user['name']}\n🪙 Sizning balingiz: {user['bal']}")

@bot.message_handler(func=lambda message: message.text == "🎁 Sovg'alar")
def show_gifts(message):
    user = get_user(message.from_user.id)
    markup = types.InlineKeyboardMarkup()
    for key, item in GIFTS.items():
        btn = types.InlineKeyboardButton(f"{item['name']} - {item['price']} ball", callback_data=f"buy_{key}")
        markup.add(btn)
    bot.send_message(message.chat.id, f"Sizda {user['bal']} ball bor. Sovg'ani tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📸 Rasm yuborish (2 ball)")
def ask_photo(message):
    bot.send_message(message.chat.id, "Iltimos, rasm yuboring. Admin tasdiqlasa ball beriladi.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Tasdiqlash ✅", callback_data=f"ok_{user_id}"),
               types.InlineKeyboardButton("Rad etish ❌", callback_data=f"no_{user_id}"))
    
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, 
                   caption=f"Foydalanuvchi: {user['name']}\nID: {user_id}", reply_markup=markup)
    bot.send_message(message.chat.id, "Rasm adminga yuborildi.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith('ok_'):
        target_id = int(call.data.split('_')[1])
        users_data[target_id]['bal'] += 2
        bot.send_message(target_id, "Rasmingiz tasdiqlandi! +2 ball ✅")
        bot.edit_message_caption("Tasdiqlandi ✅", ADMIN_ID, call.message.message_id)
        
    elif call.data.startswith('no_'):
        target_id = int(call.data.split('_')[1])
        bot.send_message(target_id, "Rasmingiz rad etildi ❌")
        bot.edit_message_caption("Rad etildi ❌", ADMIN_ID, call.message.message_id)

    elif call.data.startswith('buy_'):
        gift_key = call.data.split('_')[1]
        gift = GIFTS[gift_key]
        user = get_user(call.from_user.id)
        
        if user['bal'] >= gift['price']:
            user['bal'] -= gift['price']
            bot.answer_callback_query(call.id, "Xarid qilindi!")
            bot.send_message(call.from_user.id, f"Tabriklaymiz! {gift['name']} sotib oldingiz.")
            bot.send_message(ADMIN_ID, f"🔔 XARID!\nKim: {user['name']}\nNima: {gift['name']}")
        else:
            bot.answer_callback_query(call.id, "Ball yetarli emas!", show_alert=True)

# --- ISHGA TUSHIRISH ---
def run_bot():
    while True:
        try:
            bot.remove_webhook()
            print("Bot ishga tushdi...")
            bot.polling(none_stop=True, interval=2, timeout=20)
        except Exception as e:
            print(f"Xato: {e}")
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
