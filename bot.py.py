import telebot
import yt_dlp
import os
from keep_alive import keep_alive

# 1. من الأفضل استدعاء التوكن من متغيرات البيئة (حماية لك)
# لا تنسَ عمل Revoke للتوكن القديم من BotFather!
TOKEN = os.getenv('BOT_TOKEN', '8775190237:AAGFp6jlqlJ-lOK7PuqOD6qQlS__8NEMTi4')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك في بوت تنزيل فيديوهات يوتيوب.")

@bot.message_handler(func=lambda message: "youtu" in message.text)
def download_youtube(message):
    bot.reply_to(message, "جاري معالجة الرابط والتحميل... ⏳ (قد يستغرق الأمر بعض الوقت حسب حجم المقطع)")
    url = message.text
    
    # 2. إنشاء اسم فريد للملف باستخدام آي دي المحادثة ورقم الرسالة لمنع تداخل تحميلات المستخدمين
    unique_filename = f"video_{message.chat.id}_{message.message_id}.mp4"
    
    # إعدادات التحميل: إجبار المكتبة على ألا تتجاوز 50 ميجا (بدون السماح ببدائل أكبر)
    ydl_opts = {
        'format': 'best[ext=mp4]/best', # إزالة شرط الحجم المسبق
        'outtmpl': f"video_{message.chat.id}_{message.message_id}.mp4",
        'quiet': False, # مهم جداً: يجعل الأخطاء تظهر في Logs منصة Render لتسهيل اكتشاف المشكلة
        'noplaylist': True,
        # السطر التالي يخدع يوتيوب ويجعله يظن أن الطلب قادم من تطبيق أندرويد لتجاوز الحظر
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}} 
    }

    try:
        # تحميل المقطع
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # التأكد من أن الملف تم تحميله فعلاً
        if os.path.exists(unique_filename):
            with open(unique_filename, 'rb') as video:
                bot.send_video(message.chat.id, video, caption="تم التحميل بنجاح! ✅")
        else:
            bot.reply_to(message, "❌ عذراً، لا يوجد نسخة من هذا المقطع بحجم أقل من 50 ميجابايت.")
            
    except Exception as e:
        bot.reply_to(message, "❌ عذراً، حدث خطأ أثناء معالجة الرابط. تأكد من صحة الرابط أو أن حجم المقطع يتجاوز الحد المسموح.")
        print(f"Error: {e}")
        
    finally:
        # 3. وضع الحذف في finally يضمن مسح الفيديو في كل الحالات، حتى لو حدث خطأ أثناء الإرسال
        if os.path.exists(unique_filename):
            os.remove(unique_filename)

print("البوت يعمل الآن...")
keep_alive() 
bot.infinity_polling()
