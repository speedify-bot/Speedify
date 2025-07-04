import logging
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from yt_dlp import YoutubeDL

TOKEN = os.environ.get("BOT_TOKEN")  # توکن ربات رو از محیط بخونه

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# پیغام خوش‌آمد
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 خوش اومدی! اسم آهنگ یا لینک اسپاتیفای رو بفرست تا برات دانلود کنم.")

# دریافت پیام و دانلود آهنگ
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    msg = await update.message.reply_text("🔎 در حال جستجو و دانلود آهنگ...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'quiet': True,
        'noplaylist': True,
        'default_search': 'ytsearch',
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            file_name = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")

        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(file_name, 'rb'), title=info.get('title'), performer=info.get('uploader'))
        os.remove(file_name)
        await msg.delete()

    except Exception as e:
        await msg.edit_text("❌ خطا در دانلود آهنگ. لطفاً یک اسم یا لینک معتبر بفرست.")

# شروع ربات
if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()
