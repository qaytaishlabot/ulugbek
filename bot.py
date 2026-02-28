import telebot
from telebot import types
import os
import threading
from flask import Flask
from datetime import date
from ultralytics import YOLO
import cv2
import numpy as np
import json

# --- 1. SOZLAMALAR ---
API_TOKEN = "8615427119:AAGlCJrpNusimALpU2GaZ304x6UvjniPLgo"
ADMIN_ID = 7543961611

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- DATABASE ---
DB_FILE = "database.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return {"users": {}, "limits": {}}
    return {"users": {}, "limits": {}}

def save_data():
    with open(DB_FILE, "w") as f:
        json.dump({"users": users_data, "limits": daily_limits}, f)

data = load_data()
users_data = data.get("users", {})
daily_limits = data.get("limits", {})

# --- 2. AI MODEL ---
model = YOLO("yolov8n.pt") 

def detect_trash_type_local(path):
    results = model(path, conf=0.3)[0] # 30% aniqlik yetarli
    if len(results.boxes) == 0:
        return "none"
    
    classes = results.boxes.cls.cpu().numpy().astype(int)
    
    # 39: bottle (plastic), 73: book (paper)
    if 39 in classes: return "plastic"
    if 73 in classes: return "paper"
    
    # Agar boshqa biror narsa aniqlansa (masalan, kosa, qoshiq, quti va h.k.)
    return "other"

# --- SOVG'ALAR (O'zgarmadi) ---
GIFTS = {
    "ruchka": {"name": "🖋 Ruchka", "price": 30},
    "daftar": {"name": "📖 Daftar", "price": 50},
    "kitob": {"name": "📚 Kitob", "price": 80},
}

# --- MENULAR ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🎁 Sovg'alar", "💰 Mening ballarim")
    markup.row("📸 Rasm yuborish")
    markup.row("ℹ️ Bot haqida", "📜 Qoidalar")
    return markup

def registration_button():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 Ro'yxatdan o'tish")
    return markup

@app.route("/")
def home():
    return "Bot ishlayapti!"

# --- BOT LOGIKASI ---
@bot.message_handler(commands=["start"])
def start(message):
    uid = str(message.from_user.id)
    if uid not in users_data or not users_data[uid].get("registered"):
        bot.send_message(message.chat.id, "Xush kelibsiz! Botdan foydalanish uchun ro'yxatdan o'ting:", reply_markup=registration_button())
    else:
        bot.send_message(message.chat.id, "Asosiy menyu:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "📝 Ro'yxatdan o'tish")
def ask_name(message):
    bot.send_message(message.chat.id, "Ism va familiyangizni kiriting:")
    bot.register_next_step_handler(message, save_name_request)

def save_name_request(message):
    uid = str(message.from_user.id)
    name = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Tasdiqlash ✅", callback_data=f"reg_ok_{uid}_{name}"),
        types.InlineKeyboardButton("Rad etish ❌", callback_data=f"reg_no_{uid}")
    )
    bot.send_message(ADMIN_ID, f"Yangi so'rov:\n👤 {name}\nID: {uid}", reply_markup=markup)
    bot.send_message(message.chat.id, "So'rovingiz adminga yuborildi.")

@bot.message_handler(func=lambda m: m.text == "📸 Rasm yuborish")
def send_photo_info(message):
    bot.send_message(message.chat.id, "Chiqindini rasmga olib yuboring (Plastik, Qog'oz yoki boshqa).")

@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    uid = str(message.from_user.id)
    if uid not in users_data or not users_data[uid].get("registered"):
        bot.send_message(message.chat.id, "Avval ro'yxatdan o'ting!", reply_markup=registration_button())
        return

    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    temp_path = f"temp_{uid}.jpg"
    
    with open(temp_path, "wb") as f:
        f.write(downloaded_file)
    
    trash_type = detect_trash_type_local(temp_path)
    
    # Har qanday holatda ham adminga yuboramiz (agar AI hech narsa topmasa "other" deb ketadi)
    display_type = "Noma'lum"
    if trash_type == "plastic": display_type = "Plastik"
    elif trash_type == "paper": display_type = "Qog'oz"
    else: display_type = "Boshqa axlat"

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Tasdiqlash ✅", callback_data=f"v_ok_{uid}_{trash_type}"),
        types.InlineKeyboardButton("Rad etish ❌", callback_data=f"v_no_{uid}")
    )
    with open(temp_path, "rb") as photo:
        bot.send_photo(ADMIN_ID, photo, caption=f"Foydalanuvchi: {users_data[uid]['name']}\nAI aniqladi: {display_type}", reply_markup=markup)
    
    bot.send_message(message.chat.id, "Rasm adminga yuborildi. Tasdiqlangach ball beriladi.")
    os.remove(temp_path)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    d = call.data.split("_")
    
    if d[0] == "reg":
        uid, status = d[2], d[1]
        if status == "ok":
            name = d[3]
            users_data[uid] = {"name": name, "points": 0, "registered": True}
            save_data()
            bot.send_message(uid, f"Tasdiqlandingiz! Xush kelibsiz.", reply_markup=main_menu())
            bot.edit_message_text(f"Tasdiqlandi: {name}", call.message.chat.id, call.message.message_id)
        else:
            bot.send_message(uid, "Rad etildi.")
            bot.edit_message_text("Rad etildi.", call.message.chat.id, call.message.message_id)

    elif d[0] == "v":
        uid, status = d[2], d[1]
        if status == "ok":
            t_type = d[3]
            # YANGI BALL TIZIMI
            if t_type == "plastic": p = 2
            elif t_type == "paper": p = 2
            else: p = 1 # Boshqa hamma axlatlar uchun 1 ball
            
            users_data[uid]["points"] += p
            save_data()
            bot.send_message(uid, f"Rasm tasdiqlandi! +{p} ball. Jami: {users_data[uid]['points']}")
            bot.edit_message_caption(f"Tasdiqlandi ✅ (+{p} ball)", call.message.chat.id, call.message.message_id)
        else:
            bot.send_message(uid, "Rasm qabul qilinmadi.")
            bot.edit_message_caption("Rad etildi ❌", call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda m: m.text == "💰 Mening ballarim")
def my_points(message):
    uid = str(message.from_user.id)
    p = users_data.get(uid, {}).get("points", 0)
    bot.send_message(message.chat.id, f"Sizning ballaringiz: {p} ball 🪙")

@bot.message_handler(func=lambda m: m.text == "🎁 Sovg'alar")
def show_gifts(message):
    text = "🎁 **Sovg'alar:**\n\n"
    for k, v in GIFTS.items():
        text += f"{v['name']} — {v['price']} ball\n"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# --- ISHGA TUSHIRISH ---
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
