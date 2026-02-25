
import os
from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Render uchun server (Bot o'chib qolmasligi uchun)
app = Flask('')
@app.route('/')
def home(): return "Bot yoniq!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# 2. ASOSIY MA'LUMOTLAR
ADMIN_ID = 7543961611 
user_scores = {}  # Ballarni saqlash
user_names = {}   # Ismlarni saqlash

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['📝 Ro\'yxatdan o\'tish'],
        ['🗑 Axlat tashlash', '🎁 Sovg\'alar'],
        ['⭐ Ballarim', '🏆 Reyting'],
        ['📜 Qoidalar', 'ℹ️ Bot haqida']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Xush kelibsiz! Maqsadi tabiatni asrash bo'lgan loyihamiz botiga xush kelibsiz.", 
        reply_markup=reply_markup
    )

# 3. ADMIN UCHUN BALL BERISH (Masalan: /ball 12345 10)
async def add_ball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        u_id = int(context.args[0])
        score = int(context.args[1])
        user_scores[u_id] = user_scores.get(u_id, 0) + score
        await update.message.reply_text(f"✅ ID {u_id} ga {score} ball qo'shildi.")
    except:
        await update.message.reply_text("Xato! Namuna: /ball [ID] [miqdor]")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    uid = user.id

    if text == "📝 Ro'yxatdan o'tish":
        await update.message.reply_text("Ism va Familiyangizni yozib yuboring:")
        context.user_data['step'] = 'reg'
    
    elif text == "🏆 Reyting":
        # Faqat balli bor va ismi saqlanganlarni ko'rsatish
        active = {user_names[i]: s for i, s in user_scores.items() if s > 0 and i in user_names}
        if not active:
            await update.message.reply_text("🏆 Reyting hali shakllanmadi.")
        else:
            sorted_res = sorted(active.items(), key=lambda x: x[1], reverse=True)
            msg = "🏆 TOP O'QUVCHILAR:\n\n"
            for i, (name, score) in enumerate(sorted_res, 1):
                msg += f"{i}. {name} — {score} ball\n"
            await update.message.reply_text(msg)

    elif text == "⭐ Ballarim":
        await update.message.reply_text(f"Sizning ballingiz: {user_scores.get(uid, 0)} ball.")

    elif text == "ℹ️ Bot haqida":
        await update.message.reply_text("Maqsad: Atrof-muhitni asrash. Asoschi: Z.Ulugbek")

    elif context.user_data.get('step') == 'reg':
        user_names[uid] = text
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"📂 YANGI: {text}\n🆔 ID: {uid}")
        await update.message.reply_text("✅ Ro'yxatdan o'tdingiz!")
        context.user_data['step'] = None 
    
    else:
        await update.message.reply_text("Iltimos, menyudan foydalaning.")

if __name__ == '__main__':
    # TOKENNI ORTIQCHA JOYSIZ (PROBELSIZ) QO'YING
    TOKEN = "8615427119:AAG3rXwxXTGqvhVBzV-VSrHQllpco3CMqaQ"
    
    keep_alive()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ball", add_ball))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling(drop_pending_updates=True) # ESKI XABARLARNI O'CHIRIB TASHLASH
