import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from yt_dlp import YoutubeDL
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تنظیمات دانلود yt-dlp
YDL_OPTS = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'ignoreerrors': True,
    'cachedir': False,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

if not os.path.exists('downloads'):
    os.makedirs('downloads')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! لطفا لینک یا نام آهنگ رو بفرست تا برات دانلود کنم و بفرستم."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("کافیه لینک یا نام آهنگ رو ارسال کنی، من آهنگ رو برات میفرستم.")

async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()

    msg = await update.message.reply_text("در حال جستجو و دانلود آهنگ، لطفا صبر کن...")

    try:
        with YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(user_input, download=True)
            if info is None:
                await msg.edit_text("آهنگ پیدا نشد، لطفا لینک یا نام دقیق‌تری بفرست.")
                return
            # مسیر فایل دانلود شده
            filename = ydl.prepare_filename(info)
            # پسوند رو به mp3 تغییر دادیم بعد از تبدیل
            filename = os.path.splitext(filename)[0] + ".mp3"

        # ارسال فایل
        with open(filename, 'rb') as audio:
            await update.message.reply_audio(audio=audio, title=info.get('title', 'آهنگ'))

        await msg.delete()

    except Exception as e:
        logger.error(f"Error downloading: {e}")
        await msg.edit_text("مشکلی پیش اومد، لطفا دوباره تلاش کن.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_and_send))

    app.run_polling()

if __name__ == '__main__':
    main()
