import telebot
import yt_dlp
import os  # تم تعديل هذا السطر ليعمل أمر حذف الفيديو بنجاح
from keep_alive import keep_alive

TOKEN = '8775190237:AAGFp6jlqlJ-lOk7PuqOD6qQlS__8NEMTi4'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك في بوت تنزيل فيديوهات يوتيوب.")

@bot.message_handler(func=lambda message: "youtu" in message.text)
def download_youtube(message):
    bot.reply_to(message, "جاري معالجة الرابط والتحميل... ⏳ (قد يستغرق الأمر بعض الوقت حسب حجم المقطع)")
    url = message.text
    
    # إعدادات التحميل: جلب فيديو بصيغة mp4 بحيث لا يتجاوز 50 ميجابايت (الحد الأقصى المسموح لبوتات تليجرام)
    ydl_opts = {
        'format': 'best[ext=mp4][filesize<50M]/best',
        'outtmpl': 'video.%(ext)s',
        'quiet': True
    }
    
    try:
        # تحميل المقطع
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # إرسال المقطع إلى تليجرام
        with open('video.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video, caption="تم التحميل بنجاح! ✅")
        
        # حذف الملف من سيرفر Render بعد إرساله حتى لا تمتلئ المساحة
        os.remove('video.mp4')
        
    except Exception as e:
        bot.reply_to(message, "❌ عذراً، لا يمكن تحميل هذا المقطع. قد يكون حجمه أكبر من 50 ميجابايت (الحد الأقصى لتليجرام) أو أن الرابط غير صحيح.")
        

print("البوت يعمل الآن...")
keep_alive()
bot.infinity_polling()
