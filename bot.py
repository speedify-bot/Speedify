import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from youtubesearchpython import VideosSearch
import yt_dlp
import asyncio

# فعال‌سازی لاگ برای خطایابی
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = 'توکن_ربات_خودت_اینجا'

# هندلر اصلی پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    query = update.message.text

    await update.message.reply_text(f"🎧 {user} عزیز، دارم دنبال آهنگت می‌گردم... ⏳")

    try:
        # جستجو در یوتیوب
        search = VideosSearch(query, limit=1)
        result = search.result()['result'][0]
        title = result['title']
        link = result['link']

        await update.message.reply_text(f"🎶 پیدا کردم: *{title}*\n🔗 {link}", parse_mode='Markdown')

        # تنظیمات yt_dlp برای دانلود MP3
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'song.mp3',
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        # ارسال فایل
        await update.message.reply_audio(audio=open('song.mp3', 'rb'), caption=f"🎵 {title} آماده‌ست!")

        # حذف فایل موقت
        os.remove('song.mp3')

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("❌ متأسفم، نتونستم آهنگ رو بفرستم. دوباره امتحان کن یا یه اسم دیگه بده.")

# اجرای ربات
async def main():
    import nest_asyncio
    nest_asyncio.apply()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("ربات اجرا شد ✅")
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
