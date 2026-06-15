import telebot
import yt_dlp
import os
import imageio_ffmpeg # تم إضافة هذه المكتبة السحرية لجلب ffmpeg
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive

# تحديد مسار أداة ffmpeg تلقائياً من المكتبة لتستخدمها yt_dlp
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

# استدعاء التوكن بشكل آمن
TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك في بوت التحميل الاحترافي 🚀\nأرسل لي أي رابط من يوتيوب للبدء.")

@bot.message_handler(func=lambda message: "youtu" in message.text)
def handle_youtube_link(message):
    url = message.text
    
    # إنشاء أزرار تفاعلية (Inline Keyboard)
    markup = InlineKeyboardMarkup()
    btn_video = InlineKeyboardButton("تحميل كفيديو 🎬", callback_data=f"mp4|{url}")
    btn_audio = InlineKeyboardButton("تحميل كصوت 🎵", callback_data=f"audio|{url}")
    markup.add(btn_video, btn_audio)
    
    bot.reply_to(message, "الرابط جاهز! اختر الصيغة التي تريد التحميل بها:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    bot.answer_callback_query(call.id, "جاري معالجة طلبك... ⏳")
    
    bot.edit_message_text("جاري معالجة الرابط والتحميل... ⏳\nيرجى الانتظار...", 
                          chat_id=call.message.chat.id, 
                          message_id=call.message.message_id)
    
    data = call.data.split("|", 1)
    format_type = data[0]
    url = data[1]
    
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    
    unique_filename = f"media_{chat_id}_{msg_id}"
    
    # --- الإعدادات الجديدة والمحسنة ---
    if format_type == "mp4":
        ydl_opts = {
            # سيقوم بجلب أفضل فيديو وأفضل صوت ودمجهما، وإن فشل سيجلب أفضل صيغة متاحة
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 
            'outtmpl': unique_filename + '.%(ext)s',
            'noplaylist': True,
            'cookiefile': 'cookies.txt',
            'ffmpeg_location': ffmpeg_path, # ربط ffmpeg بالعملية
            'quiet': True,
            'no_warnings': True
        }
    else: # صوت
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': unique_filename + '.%(ext)s',
            'noplaylist': True,
            'cookiefile': 'cookies.txt',
            'ffmpeg_location': ffmpeg_path, # ربط ffmpeg بالعملية
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }] # تحويل الصوت مباشرة إلى mp3
        }

    downloaded_file = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # بما أننا حولنا الصوت إلى mp3، نحدد الامتداد الجديد
            if format_type == 'audio':
                ext = 'mp3'
            else:
                ext = info.get('ext', 'mp4')
                
            downloaded_file = f"{unique_filename}.{ext}"
        
        if os.path.exists(downloaded_file):
            with open(downloaded_file, 'rb') as file:
                if format_type == "mp4":
                    bot.send_video(chat_id, file, caption="تم التحميل بنجاح! ✅")
                else:
                    bot.send_audio(chat_id, file, caption="تم التحميل بنجاح! ✅")
            
            bot.delete_message(chat_id, msg_id) 
        else:
            bot.edit_message_text("❌ حدثت مشكلة، لم يتم العثور على الملف بعد التحميل.", chat_id=chat_id, message_id=msg_id)

    except Exception as e:
        error_msg = str(e).split('\n')[0][:200]
        bot.edit_message_text(f"❌ عذراً، فشل التحميل.\nالسبب التقني:\n{error_msg}", chat_id=chat_id, message_id=msg_id)
        
    finally:
        if downloaded_file and os.path.exists(downloaded_file):
            os.remove(downloaded_file)
        for f in os.listdir('.'):
            if f.startswith(unique_filename):
                os.remove(f)

print("البوت يعمل الآن...")
keep_alive() 
bot.infinity_polling()
