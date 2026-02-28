import telebot
from telebot import types
import os
import threading
from flask import Flask
from datetime import date
from ultralytics import YOLO
import cv2
import numpy as np

# --- 1. SOZLAMALAR ---
# Tokenni to'g'ridan-to'g'ri shu yerga yozamiz (Render sozlamalariga bog'liq bo'lmasligi uchun)
API_TOKEN = "8615427119:AAGlCJrpNusimALpU2GaZ304x6UvjniPLgo"
ADMIN_ID = 7543961611

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__) # __name__ xatosi tuzatildi

# --- Foydalanuvchi + limit bazasi ---
users_data = {}
daily_limits = {}
MAX_DAILY = 3

# --- Sovg'alar ---
GIFTS = {
    "ruchka": {"name": "🖋 Ruchka", "price": 30},
    "daftar": {"name": "📖 Daftar", "price": 50},
    "kitob": {"name": "📚 Kitob", "price": 80},
}

@app.route("/")
def home():
    return "Bot ishlayapti!"

# --- MODELNI YUKLASH ---
model = YOLO("best.pt")

def detect_trash_type_local(path):
    results = model(path)[0]
    if len(results.boxes) == 0:
        return "none"
    classes = results.boxes.cls.cpu().numpy().astype(int)
    if 0 in classes:
        return "plastic"
    if 1 in classes:
        return "paper"
    if 2 in classes:
        return "other"
    return "none"

# --- MENU TUGMALARI ---
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

# --- BOSHLASH / RO‘YXAT ---
@bot.message_handler(commands=["start"])
def start(message):
    uid = message.from_user.id
    if uid not in users_data or not users_data[uid].get("registered"):
        bot.send_message(message.chat.id, "Ro'yxatdan o'ting:", reply_markup=registration_button())
    else:
        bot.send_message(message.chat.id, "Asosiy menyu:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "📝 Ro'yxatdan o'tish")
def ask_name(message):
    bot.send_message(message.chat.id, "Ism va familiyangizni kiriting:")
    bot.register_next_step_handler(message, save_name)

def save_name(message):
    uid = message.from_user.id
    name = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Tasdiqlash ✅", callback_data=f"reg_ok_{uid}_{name}"),
        types.InlineKeyboardButton("Rad etish ❌", callback_data=f"reg_no_{uid}")
    )
    bot.send_message(ADMIN_ID, f"Ro'yxatdan o'tish:\n👤 {name}\nID: {uid}", reply_markup=markup)
    bot.send_message(message.chat.id, "Admin tasdiqlaydi...")

# --- RASM QABUL QILISH ---
@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    uid = message.from_user.id
    if uid not in users_data or not users_data[uid].get("registered"):
        bot.send_message(message.chat.id, "Avval ro'yxatdan o'ting!") # .chat.id tuzatildi
        return

    today = str(date.today())
    if uid not in daily_limits or daily_limits[uid]["date"] != today:
        daily_limits[uid] = {"date": today, "used": 0}
    if daily_limits[uid]["used"] >= MAX_DAILY:
        bot.send_message(message.chat.id, "Bugun limit tugadi (3 rasm).")
        return

    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded = bot.download_file(file_info.file_path)
    
    # Papka muammosini oldini olish
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
        
    path = f"tmp/{file_id}.jpg"
    with open(path, "wb") as f:
        f.write(downloaded)

    trash_type = detect_trash_type_local(path)
    if trash_type == "none":
        bot.send_message(message.chat.id, "Axlat aniqlanmadi. Iltimos, qayta yuboring.")
        os.remove(path)
        return

    pts = 2 if trash_type in ["plastic","paper"] else 1
    users_data[uid]["bal"] += pts
    daily_limits[uid]["used"] += 1

    bot.send_message(
        message.chat.id,
        f"Axlat turi: {trash_type}\n+{pts} ball!\nLimit: {daily_limits[uid]['used']}/3"
    )
    os.remove(path)

# --- MATN TUGMALARI ---
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    if uid not in users_data or not users_data[uid].get("registered"):
        bot.send_message(message.chat.id, "Ro'yxatdan o'ting.", reply_markup=registration_button())
        return
    if message.text == "💰 Mening ballarim":
        bot.send_message(message.chat.id, f"Ballaringiz: {users_data[uid]['bal']}")
    elif message.text == "🎁 Sovg'alar":
        markup = types.InlineKeyboardMarkup()
        for k,v in GIFTS.items():
            markup.add(types.InlineKeyboardButton(f"{v['name']} - {v['price']} ball", callback_data=f"buy_{k}"))
        bot.send_message(message.chat.id, "Sovg'ani tanlang:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "🤖 Noma’lum buyruq.")

# --- CALLBACK ---
@bot.callback_query_handler(func=lambda call: True)
def cb(call):
    d = call.data
    if d.startswith("reg_ok_"):
        parts = d.split("_")
        uid = int(parts[2])
        nm = parts[3]
        users_data[uid] = {"registered": True, "bal": 0, "name": nm}
        bot.send_message(uid, "Tasdiqlandi! 🎉", reply_markup=main_menu())
        bot.edit_message_text("Tasdiqlandi ✅", ADMIN_ID, call.message.message_id)
    elif d.startswith("buy_"):
        g = d.split("_")[1]
        uid = call.from_user.id
        price = GIFTS[g]["price"]
        if users_data[uid]["bal"] >= price:
            users_data[uid]["bal"] -= price
            bot.send_message(uid, f"Sovg'a: {GIFTS[g]['name']} 🎁")
        else:
            bot.answer_callback_query(call.id, "Ball yetarli emas!")

# --- BOTNI ISHGA TUSHIRISH ---
def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__": # __name__ tuzatildi
    threading.Thread(target=run_bot).start()
    # Render portini avtomatik olish
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
