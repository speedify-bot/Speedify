import os
import asyncio
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from youtubesearchpython import VideosSearch
import yt_dlp
import ffmpeg

BOT_TOKEN = 'توکن_ربات_تو_اینجا_قرار_بده'

# مسیر پوشه دانلود موقت
DOWNLOAD_PATH = './downloads'
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک یا نام آهنگ رو بفرست تا برات دانلود کنم.")

def search_youtube(song_name):
    videosSearch = VideosSearch(song_name, limit=1)
    result = videosSearch.result()
    video_url = result['result'][0]['link']
    title = result['result'][0]['title']
    return video_url, title

def download_audio(url, file_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': file_path,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    msg = await update.message.reply_text("در حال جستجو و دانلود آهنگ... لطفا صبر کن.")
    
    try:
        video_url, title = search_youtube(user_input)
    except Exception:
        await msg.edit_text("متاسفم، نتونستم آهنگ رو پیدا کنم.")
        return

    file_name = title.replace(' ', '_') + '.mp3'
    file_path = os.path.join(DOWNLOAD_PATH, file_name)

    try:
        download_audio(video_url, file_path)
    except Exception:
        await msg.edit_text("مشکلی در دانلود آهنگ پیش آمد.")
        return

    try:
        with open(file_path, 'rb') as audio_file:
            await update.message.reply_audio(audio_file, title=title)
        await msg.delete()
    except Exception:
        await msg.edit_text("مشکلی در ارسال آهنگ پیش آمد.")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
