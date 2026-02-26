import telebot
from telebot import types

# Botingiz tokeni o'rnatildi
TOKEN = '8615427119:AAG3rXwxXTGqvhVBzV-VSrHQllpco3CMqaQ'
bot = telebot.TeleBot(TOKEN)

# Start komandasi va menyuni yaratish
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    # Tugmalar rasmda ko'ringandek tartibda
    btn1 = types.KeyboardButton("📝 Ro'yxatdan o'tish")
    btn2 = types.KeyboardButton("🗑 Axlat tashlash")
    btn3 = types.KeyboardButton("🎁 Sovg'alar")
    btn4 = types.KeyboardButton("⭐ Ballarim")
    btn5 = types.KeyboardButton("📜 Qoidalar")
    btn6 = types.KeyboardButton("ℹ️ Bot haqida")
    btn7 = types.KeyboardButton("🏆 Reyting")
    
    # Tugmalarni joylashtirish
    markup.add(btn1)
    markup.add(btn2, btn3)
    markup.add(btn4, btn7)
    markup.add(btn5, btn6)
    
    bot.send_message(message.chat.id, "Xush kelibsiz! Kerakli bo'limni tanlang:", reply_markup=markup)

# Tugmalarni tutib olish
@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    # Har bir shart tugmadagi matn va emoji bilan aynan bir xil
    
    if message.text == "🗑 Axlat tashlash":
        bot.send_message(message.chat.id, "Iltimos, axlatni rasmga olib yuboring! 📸 Adminlar tekshirgach, sizga ball beriladi.")
        
    elif message.text == "🎁 Sovg'alar":
        sovgalar_text = (
            "🎁 Sovg'alar ro'yxati:\n\n"
            "• 30 ball — Ruchka 🖊\n"
            "• 50 ball — Daftar 📓\n"
            "• 75 ball — Kitob 📚\n\n"
            "Ballaringiz yetarli bo'lganda admin bilan bog'laning!"
        )
        bot.send_message(message.chat.id, sovgalar_text)
        
    elif message.text == "📜 Qoidalar":
        qoidalar_text = (
            "📜 Botdan foydalanish qoidalari:\n\n"
            "1. Axlatni maxsus joyga tashlang va rasmga oling.\n"
            "2. Rasmni botga yuboring (haqqoniy bo'lsin).\n"
            "3. Adminlar tekshirgach, hisobingizga ball qo'shiladi.\n"
            "4. To'plangan ballarni sovg'alarga almashtiring!"
        )
        bot.send_message(message.chat.id, qoidalar_text)
        
    elif message.text == "⭐ Ballarim":
        # Hozircha statik 0 ball, bazani ulaganingizda bu qism o'zgaradi
        bot.send_message(message.chat.id, "Sizning hozirgi ballingiz: 0 ball. ⭐")
        
    elif message.text == "ℹ️ Bot haqida":
        bot.send_message(message.chat.id, "Maqsad: Atrof-muhitni asrash va yoshlarni rag'batlantirish.\nAsoschi: Z.Ulugbek")
        
    elif message.text == "🏆 Reyting":
        bot.send_message(message.chat.id, "🏆 Reyting shakllantirilmoqda. Tez orada eng faol foydalanuvchilarni ko'rishingiz mumkin.")

    elif message.text == "📝 Ro'yxatdan o'tish":
        bot.send_message(message.chat.id, "Ism va familiyangizni yuboring (masalan: Ali Valiyev).")

    else:
        # Agar tugmadan tashqari narsa yozilsa
        bot.send_message(message.chat.id, "Iltimos, pastdagi menyu tugmalaridan foydalaning.")

# Botni ishga tushirish
if __name__ == "__main__":
    print("Bot Render serverida ishga tushishga tayyor...")
    bot.infinity_polling()
