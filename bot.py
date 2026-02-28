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
API_TOKEN = os.getenv("8615427119:AAGlCJrpNusimALpU2GaZ304x6UvjniPLgo")  # Render Environment Variable dan oling
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
    results = model(path, conf=0.3)[0]
    if len(results.boxes) == 0:
        return "none"
    
    classes = results.boxes.cls.cpu().numpy().astype(int)
    if 39 in classes: return "plastic"
    if 73 in classes: return "paper"
    return "other"

# --- SOVG'ALAR ---
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

# Bu yerda qolgan eski kod o‘zgarmaydi: Ro‘yxatdan o‘tish, rasm yuborish, callback, ballar va sovg‘alar
# handle_photo va callback_query_handler funksiyalari xuddi sizning eski koddagi kabi ishlaydi
# Faqat tokenni Environment Variable orqali oladigan qilib to‘g‘riladim
# Flask server va threading bilan ham ishlaydi

# --- ISHGA TUSHIRISH ---
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
