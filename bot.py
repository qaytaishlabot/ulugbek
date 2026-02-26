import telebot
from telebot import types

# --- SOZLAMALAR ---
API_TOKEN = '8615427119:AAF44PaCDQCHIMHfzOGkx_QMGJCAaxrUBGA' # Bu yerga botfather bergan tokenni qo'ying
ADMIN_ID = 7543961611  # Sizning ID raqamingiz joylandi
bot = telebot.TeleBot(API_TOKEN)

# Foydalanuvchi ma'lumotlarini saqlash
users_data = {}

# Sovg'alar ro'yxati
GIFTS = {
    "ruchka": {"name": "🖋 Ruchka", "price": 30},
    "daftar": {"name": "📖 Daftar", "price": 50},
    "kitob":  {"name": "📚 Kitob", "price": 80}
}

def get_user_data(user_id):
    if user_id not in users_data:
        users_data[user_id] = {'bal': 0}
    return users_data[user_id]

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🎁 Sovg'alar", "💰 Mening ballarim")
    markup.row("📸 Rasm yuborish (2 ball)")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    get_user_data(message.from_user.id)
    bot.send_message(message.chat.id, "Xush kelibsiz! Kerakli bo'limni tanlang:", reply_markup=main_menu())

# --- SOVG'ALAR BO'LIMI ---
@bot.message_handler(func=lambda message: message.text == "🎁 Sovg'alar")
def gifts_menu(message):
    user = get_user_data(message.from_user.id)
    markup = types.InlineKeyboardMarkup()
    
    for key, item in GIFTS.items():
        btn = types.InlineKeyboardButton(
            text=f"{item['name']} — {item['price']} ball", 
            callback_data=f"buy_{key}"
        )
        markup.add(btn)
    
    bot.send_message(
        message.chat.id, 
        f"Sizning joriy balingiz: {user['bal']} 🪙\n\nSovg'ani tanlang:", 
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "💰 Mening ballarim")
def my_balance(message):
    user = get_user_data(message.from_user.id)
    bot.send_message(message.chat.id, f"Sizning joriy balingiz: {user['bal']} 🪙")

@bot.message_handler(func=lambda message: message.text == "📸 Rasm yuborish (2 ball)")
def ask_photo(message):
    bot.send_message(message.chat.id, "Iltimos, rasmni yuboring. Admin tasdiqlasa, 2 ball beriladi.")

# --- RASM QABUL QILISH ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    markup = types.InlineKeyboardMarkup()
    btn_yes = types.InlineKeyboardButton("Tasdiqlash ✅", callback_data=f"accept_{user_id}")
    btn_no = types.InlineKeyboardButton("Rad etish ❌", callback_data=f"reject_{user_id}")
    markup.add(btn_yes, btn_no)
    
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, 
                   caption=f"Foydalanuvchi: {user_name}\nID: {user_id}\nTasdiqlaysizmi?", 
                   reply_markup=markup)
    bot.send_message(message.chat.id, "Rasm yuborildi, admin javobini kuting.")

# --- CALLBACKLARNI BOSHQARISH ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    user = get_user_data(user_id)

    # Admin rasmni tasdiqlashi/rad etishi
    if call.data.startswith('accept_') or call.data.startswith('reject_'):
        action, target_id = call.data.split('_')
        target_id = int(target_id)
        
        if action == 'accept':
            users_data[target_id]['bal'] += 2
            bot.send_message(target_id, "Rasmingiz tasdiqlandi! +2 ball qo'shildi. ✅")
            bot.edit_message_caption(caption="Tasdiqlandi ✅", chat_id=ADMIN_ID, message_id=call.message.message_id)
        else:
            bot.send_message(target_id, "Rasmingiz rad etildi. ❌")
            bot.edit_message_caption(caption="Rad etildi ❌", chat_id=ADMIN_ID, message_id=call.message.message_id)

    # Sovg'a sotib olish
    elif call.data.startswith('buy_'):
        gift_key = call.data.split('_')[1]
        gift = GIFTS[gift_key]
        
        if user['bal'] >= gift['price']:
            user['bal'] -= gift['price']
            
            bot.answer_callback_query(call.id, "Xaridingiz muvaffaqiyatli!")
            bot.send_message(user_id, f"Tabriklaymiz! Siz {gift['name']} sotib oldingiz. \nQolgan balingiz: {user['bal']} 🪙")
            
            # Sizga (Adminga) bildirishnoma boradi
            bot.send_message(ADMIN_ID, f"🔔 **Yangi buyurtma!**\n\nFoydalanuvchi: {call.from_user.first_name}\nID: {user_id}\nSovg'a: {gift['name']}")
        else:
            bot.answer_callback_query(call.id, f"Balingiz yetarli emas! Sizga yana {gift['price'] - user['bal']} ball kerak. ❌", show_alert=True)

if __name__ == "__main__":
    print("Bot muvaffaqiyatli ishga tushdi...")
    bot.polling(none_stop=True)

