import os
from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Render server
app = Flask('')
@app.route('/')
def home(): return "Bot yoniq!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# 2. Sozlamalar
ADMIN_ID = 7543961611 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['📝 Ro\'yxatdan o\'tish'], ['📜 Qoidalar', 'ℹ️ Bot haqida']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Xush kelibsiz! Botdan foydalanish uchun tugmalardan birini tanlang.",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    if text == "📝 Ro'yxatdan o'tish":
        await update.message.reply_text(
            "Iltimos, ma'lumotlaringizni quyidagi namunada yozib yuboring:\n\n"
            "Ism: Alisher\n"
            "Familiya: Olimov\n"
            "Sinf: 9-A"
        )
    
    elif text == "📜 Qoidalar":
        await update.message.reply_text("♻️ Qoidalar: Atrof-muhitni asrang!")
        
    elif text == "ℹ️ Bot haqida":
        await update.message.reply_text("Bu qayta ishlash loyihasi botining sinov varianti.")

    # Agar xabarda "Ism:" yoki "Sinf:" so'zi bo'lsa, demak bu anketa
    elif "Ism:" in text or "Sinf:" in text:
        # SIZGA YUBORISH
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📂 YANGI ANKETA KELDI:\n\nKimdan: @{user.username}\nID: {user.id}\n\nMATN:\n{text}"
        )
        await update.message.reply_text("✅ Ma'lumotlaringiz qabul qilindi va adminga yuborildi!")
    
    else:
        await update.message.reply_text("Tushunmadim. Iltimos, menyudan foydalaning.")

if __name__ == '__main__':
    TOKEN = "8615427119:AAG3rXwxXTGqvhVBzV-VSrHQllpco3CMqaQ"
    keep_alive()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

