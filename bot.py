import os
from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Render uchun Flask server
app = Flask('')

@app.route('/')
def home():
    return "Bot yoniq!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. ADMIN SOZLAMASI
ADMIN_ID = 7543961611  # Sizning ID raqamingiz

# 3. Bot funksiyalari
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # SIZGA XABAR YUBORISH (Ro'yxat o'rniga)
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔔 Yangi foydalanuvchi!\n👤 Ismi: {user.first_name}\n🆔 ID: {user.id}\n🔗 Username: @{user.username}"
        )
    except Exception as e:
        print(f"Admin xabarni ololmadi: {e}")

    # Foydalanuvchiga javob
    keyboard = [['📜 Qoidalar', '⭐ Ballarim'], ['🗑 Axlat tashlash', 'ℹ️ Bot haqida']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"Salom {user.first_name}! Bot 24/7 rejimida ishlamoqda. Kerakli bo'limni tanlang:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📜 Qoidalar":
        await update.message.reply_text("♻️ Qoidalar: Atrof-muhitni asrang va axlatlarni saralab topshiring!")
    elif text == "⭐ Ballarim":
        await update.message.reply_text("📊 Sizning ballaringiz: 0\n(Tez kunda ballar tizimi ishga tushadi)")
    elif text == "ℹ️ Bot haqida":
        await update.message.reply_text("Bu bot chiqindilarni qayta ishlashga yordam berish uchun yaratilgan.")
    else:
        await update.message.reply_text("Iltimos, menyudagi tugmalardan foydalaning.")

if __name__ == '__main__':
    TOKEN = "8615427119:AAG3rXwxXTGqvhVBzV-VSrHQllpco3CMqaQ"
    
    keep_alive()
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot ishga tushdi...")
    application.run_polling()

