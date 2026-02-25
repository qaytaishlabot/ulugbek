import os
from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Render portini ushlab turish uchun Flask server
app = Flask('')

@app.route('/')
def home():
    return "Bot yoniq!"

def run():
    # Render 10000-portni kutadi
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. Botingiz funksiyalari
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['📜 Qoidalar', '⭐ Ballarim'], ['🗑 Axlat tashlash', 'ℹ️ Bot haqida']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Bot 24/7 rejimida ishga tushdi!", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📜 Qoidalar":
        await update.message.reply_text("Qoidalar: Tozalikka rioya qiling!")
    elif text == "⭐ Ballarim":
        await update.message.reply_text("Ballaringiz: 0")
    # ... qolgan tugmalarni ham shu tariqa qo'shishingiz mumkin

if __name__ == '__main__':
    TOKEN = "8615427119:AAG3rXwxXGqvhVBzV-VSrHQllpco3CMqaQ"
    
    # Flaskni alohida oqimda yoqamiz
    keep_alive()
    
    # Botni ishga tushiramiz
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()
