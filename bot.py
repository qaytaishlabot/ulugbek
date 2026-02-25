import os
from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

app = Flask('')
@app.route('/')
def home(): return "Bot yoniq!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# ADMIN ID
ADMIN_ID = 7543961611 

# Ballarni saqlash uchun (Vaqtinchalik xotira)
# Kelajakda buni Database-ga ulaymiz
user_scores = {
    "Ulug'bek": 150,
    "Ali": 120,
    "Vali": 90,
    "Sardor": 200
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['📝 Ro\'yxatdan o\'tish'],
        ['🗑 Axlat tashlash', '🎁 Sovg\'alar'],
        ['⭐ Ballarim', '🏆 Reyting'],
        ['📜 Qoidalar', 'ℹ️ Bot haqida']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Xush kelibsiz! Loyihamiz reyting tizimi bilan yanada qiziqarli. Tanlang:", 
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    if text == "📝 Ro'yxatdan o'tish":
        await update.message.reply_text("Iltimos, Ism va Familiyangizni yozib yuboring:")
        context.user_data['step'] = 'waiting_name'
    
    elif text == "🗑 Axlat tashlash":
        await update.message.reply_text("Rasmga olib yuboring, admin tasdiqlasa ball beriladi!")

    elif text == "🎁 Sovg'alar":
        await update.message.reply_text("🎁 Sovg'alar ro'yxati:\n1. Bloknot - 500 ball\n2. Ruchka - 200 ball")

    elif text == "⭐ Ballarim":
        # Hozircha namunaviy ball
        await update.message.reply_text(f"Sizning hozirgi ballingiz: 0 ball.")

    elif text == "🏆 Reyting":
        # Ballarni saralab chiqamiz
        sorted_scores = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
        reyting_msg = "🏆 TOP O'QUVCHILAR:\n\n"
        for i, (name, score) in enumerate(sorted_scores, 1):
            reyting_msg += f"{i}. {name} — {score} ball\n"
        await update.message.reply_text(reyting_msg)

    elif text == "📜 Qoidalar":
        await update.message.reply_text("♻️ Atrof-muhitni asrang!")
        
    elif text == "ℹ️ Bot haqida":
        await update.message.reply_text("Maqsadi: Atrof-muhitni asrash. Asoschi: Z.Ulugbek")

    elif context.user_data.get('step') == 'waiting_name':
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"📂 YANGI: {text}\nID: {user.id}")
        await update.message.reply_text("✅ Ma'lumotlaringiz yuborildi.")
        context.user_data['step'] = None 

if __name__ == '__main__':
    TOKEN = "8615427119:AAG3rXwxXTGqvhVBzV-VSrHQllpco3CMqaQ"
    keep_alive()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()
