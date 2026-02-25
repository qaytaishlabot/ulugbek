import os
from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Render server qismi
app = Flask('')
@app.route('/')
def home(): return "Bot yoniq!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# 2. Admin ID (Sizning profilingiz)
ADMIN_ID = 7543961611 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Tugmalar tartibi
    keyboard = [
        ['📝 Ro\'yxatdan o\'tish'],
        ['📜 Qoidalar', 'ℹ️ Bot haqida']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Assalomu alaykum! Loyihamiz botiga xush kelibsiz. Kerakli bo'limni tanlang:", 
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # Ro'yxatdan o'tish tugmasi bosilganda
    if text == "📝 Ro'yxatdan o'tish":
        await update.message.reply_text("Iltimos, Ism va Familiyangizni yozib yuboring:")
        context.user_data['step'] = 'waiting_name'
    
    # Qoidalar bo'limi
    elif text == "📜 Qoidalar":
        await update.message.reply_text("♻️ Qoidalar: Atrof-muhitni asrang, chiqindilarni saralang va tabiatga g'amxo'rlik qiling!")
        
    # Bot haqida bo'limi (Siz aytgan matn)
    elif text == "ℹ️ Bot haqida":
        await update.message.reply_text(
            "Bu botning maqsadi atrof-muhitni asrab-avaylash va o'quvchilarni xursand qilish uchun yaratilgan.\n\n"
            "👤 Asoschi: Z.Ulugbek"
        )

    # Foydalanuvchi ma'lumot yozganida (Admin'ga yuborish)
    elif context.user_data.get('step') == 'waiting_name':
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📂 YANGI RO'YXATDAN O'TGAN:\n👤 Ism-Familiya: {text}\n🔗 Username: @{user.username}\n🆔 ID: {user.id}"
        )
        await update.message.reply_text("✅ Rahmat! Ma'lumotlaringiz muvaffaqiyatli yuborildi.")
        context.user_data['step'] = None 
    
    else:
        await update.message.reply_text("Iltimos, pastdagi menyu tugmalaridan foydalaning.")

if __name__ == '__main__':
    # Tokenni o'zingizniki bilan tekshirib oling
    TOKEN = "8615427119:AAG3rXwxXTGqvhVBzV-VSrHQllpco3CMqaQ"
    
    keep_alive()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

