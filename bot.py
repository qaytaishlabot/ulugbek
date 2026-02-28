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
# Render-dagi Environment Variable nomi bilan bir xil qildim (API_TOKEN)
API_TOKEN = os.getenv("API_TOKEN") 
ADMIN_ID = 7543961611

# Token yo'qligida xato bermasligi uchun tekshiruv
if not API_TOKEN:
    print("XATO: API_TOKEN topilmadi! Render-da 'Environment Variables' bo'limini tekshiring.")
    bot = None
else:
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

data = load_data()
users_data = data.get("users", {})
daily_limits = data.get("limits", {})

def save_data():
    with open(DB_FILE, "w") as f:
        json.dump({"users": users_data, "limits": daily_limits}, f, indent=4)

# --- 2. AI MODEL ---
# Modelni yuklash (Render-da birinchi marta o'zi yuklab oladi)
print("YOLOv8n yuklanmoqda...")
model = YOLO("yolov8n.pt") 

def detect_trash_type_local(path):
    results = model(path, conf=0.3)[0]
    if len(results.boxes) == 0:
        return "none"
    
    classes = results.boxes.cls.cpu().numpy().astype(int)
    # YOLO klasslari bo'yicha (masalan, 39 - butilka/plastik)
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
if bot:
    @bot.message_handler(commands=["start"])
    def start(message):
        uid = str(message.from_user.id)
        if uid not in users_data or not users_data[uid].get("registered"):
            bot.send_message(message.chat.id, "Xush kelibsiz! Botdan foydalanish uchun ro'yxatdan o'ting:", reply_markup=registration_button())
        else:
            bot.send_message(message.chat.id, "Asosiy menyu:", reply_markup=main_menu())

    @bot.message_handler(func=lambda m: m.text == "📝 Ro'yxatdan o'tish")
    def register(message):
        uid = str(message.from_user.id)
        users_data[uid] = {"registered": True, "points": 0, "name": message.from_user.first_name}
        save_data()
        bot.send_message(message.chat.id, "Tabriklaymiz! Ro'yxatdan o'tdingiz.", reply_markup=main_menu())

    @bot.message_handler(func=lambda m: m.text == "💰 Mening ballarim")
    def show_points(message):
        uid = str(message.from_user.id)
        points = users_data.get(uid, {}).get("points", 0)
        bot.send_message(message.chat.id, f"Sizning jami ballaringiz: {points}")

    @bot.message_handler(content_types=['photo'])
    def handle_photo(message):
        uid = str(message.from_user.id)
        bot.send_message(message.chat.id, "Rasm tahlil qilinmoqda...")
        
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open("temp_img.jpg", "wb") as f:
            f.write(downloaded_file)
            
        trash_type = detect_trash_type_local("temp_img.jpg")
        
        if trash_type != "none":
            users_data[uid]["points"] = users_data.get(uid, {}).get("points", 0) + 5
            save_data()
            bot.send_message(message.chat.id, f"Topildi: {trash_type}! Sizga 5 ball berildi.")
        else:
            bot.send_message(message.chat.id, "Hech narsa topilmadi.")

# --- ISHGA TUSHIRISH ---
def run_bot():
    if bot:
        bot.infinity_polling()

if __name__ == "__main__":
    # Botni alohida oqimda yurgizish
    threading.Thread(target=run_bot, daemon=True).start()
    # Flaskni port orqali ishga tushirish (Render talabi)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
