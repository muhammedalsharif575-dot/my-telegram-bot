import telebot
import yt_dlp
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive

# استدعاء التوكن بشكل آمن
TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك في بوت التحميل الاحترافي 🚀\nأرسل لي أي رابط من يوتيوب للبدء.")

@bot.message_handler(func=lambda message: "youtu" in message.text)
def handle_youtube_link(message):
    url = message.text
    
    # 1. إنشاء أزرار تفاعلية (Inline Keyboard)
    markup = InlineKeyboardMarkup()
    btn_video = InlineKeyboardButton("تحميل كفيديو (MP4) 🎬", callback_data=f"mp4|{url}")
    btn_audio = InlineKeyboardButton("تحميل كصوت 🎵", callback_data=f"audio|{url}")
    markup.add(btn_video, btn_audio)
    
    bot.reply_to(message, "الرابط جاهز! اختر الصيغة التي تريد التحميل بها:", reply_markup=markup)

# 2. التعامل مع ضغطات الأزرار
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    # إيقاف علامة التحميل في الزر
    bot.answer_callback_query(call.id, "جاري معالجة طلبك... ⏳")
    
    # تعديل رسالة البوت بدلاً من إرسال رسالة جديدة
    bot.edit_message_text("جاري معالجة الرابط والتحميل... ⏳\nيرجى الانتظار...", 
                          chat_id=call.message.chat.id, 
                          message_id=call.message.message_id)
    
    # استخراج نوع الصيغة والرابط من الزر
    data = call.data.split("|", 1)
    format_type = data[0]
    url = data[1]
    
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    
    unique_filename = f"media_{chat_id}_{msg_id}"
    
    # إعدادات التحميل بناءً على اختيار المستخدم
    if format_type == "mp4":
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': unique_filename + '.%(ext)s',
            'noplaylist': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
        }
    else: # صوت
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio', # اخترنا m4a لأنها تعمل مباشرة كرسالة صوتية في تيليجرام بدون برامج إضافية
            'outtmpl': unique_filename + '.%(ext)s',
            'noplaylist': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
        }

    downloaded_file = None
    try:
        # عملية التحميل
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = info.get('ext', 'mp4') if format_type == 'mp4' else info.get('ext', 'm4a')
            downloaded_file = f"{unique_filename}.{ext}"
        
        # عملية الإرسال للمستخدم
        if os.path.exists(downloaded_file):
            with open(downloaded_file, 'rb') as file:
                if format_type == "mp4":
                    bot.send_video(chat_id, file, caption="تم التحميل بنجاح! ✅")
                else:
                    bot.send_audio(chat_id, file, caption="تم التحميل بنجاح! ✅")
            
            # حذف رسالة "جاري التحميل" لتنظيف المحادثة
            bot.delete_message(chat_id, msg_id) 
        else:
            bot.edit_message_text("❌ حدثت مشكلة، لم يتم العثور على الملف بعد التحميل.", chat_id=chat_id, message_id=msg_id)

    except Exception as e:
        # طباعة الخطأ الفعلي لكي نعرف إذا كان يوتيوب قد حظرنا
        error_msg = str(e).split('\n')[0][:100]
        bot.edit_message_text(f"❌ عذراً، فشل التحميل.\nالسبب التقني:\n{error_msg}", chat_id=chat_id, message_id=msg_id)
        
    finally:
        # تنظيف وحذف الملفات من سيرفر Render لتوفير المساحة
        if downloaded_file and os.path.exists(downloaded_file):
            os.remove(downloaded_file)
        for f in os.listdir('.'):
            if f.startswith(unique_filename):
                os.remove(f)

print("البوت الاحترافي يعمل الآن...")
keep_alive() 
bot.infinity_polling()
