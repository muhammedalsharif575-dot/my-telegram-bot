import telebot
from keep_alive import keep_alive

TOKEN = '8775190237:AAGFp6jlqlJ-lOK7PuqOD6qQlS__8NEMTi4'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك في بوت دليل القبول! أنا جاهز لمساعدتك.")

print("البوت يعمل الآن...")
keep_alive()
bot.infinity_polling()
