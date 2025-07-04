import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import requests

# بارگذاری توکن‌ها از متغیرهای محیطی
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

if not TELEGRAM_TOKEN:
    print("Error: TELEGRAM_TOKEN not set!")
    exit(1)
if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    print("Error: Spotify credentials not set!")
    exit(1)

# راه‌اندازی اسپاتیفای
spotify = Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

# تابع کمکی برای استخراج نام و خواننده از لینک اسپاتیفای
def get_spotify_track_info(url: str):
    try:
        track_id = url.split("track/")[1].split("?")[0]
        track = spotify.track(track_id)
        name = track['name']
        artists = ", ".join([artist['name'] for artist in track['artists']])
        return f"{name} - {artists}"
    except Exception as e:
        return None

# تابع دانلود آهنگ از یوتیوب با کیفیت انتخابی
def download_audio(youtube_query, quality="bestaudio"):
    ydl_opts = {
        'format': f'bestaudio[ext=m4a]/bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320' if quality == '320' else '128',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{youtube_query}", download=True)
        filename = ydl.prepare_filename(info['entries'][0])
        audio_file = filename.rsplit(".", 1)[0] + ".mp3"
        return audio_file, info['entries'][0]['title']

# هندلر شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک اسپاتیفای، ساندکلود یا اینستاگرام آهنگ بفرست تا با بهترین کیفیت برات ارسال کنم.")

# هندلر پیام متنی (لینک آهنگ)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    chat_id = update.message.chat_id

    # تشخیص لینک اسپاتیفای
    if "open.spotify.com/track/" in text:
        info = get_spotify_track_info(text)
        if info is None:
            await update.message.reply_text("لینک اسپاتیفای معتبر نیست یا خطایی رخ داده.")
            return
        query = info
    else:
        # برای سادگی، اسم آهنگ رو مستقیم لینک یا متن بفرست
        query = text

    # کیبرد انتخاب کیفیت
    keyboard = [
        [InlineKeyboardButton("MP3 128", callback_data=f"download|{query}|128")],
        [InlineKeyboardButton("MP3 320", callback_data=f"download|{query}|320")],
        [InlineKeyboardButton("FLAC (در صورت موجود بودن)", callback_data=f"download|{query}|flac")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"آهنگ «{query}» رو با چه کیفیتی می‌خوای؟", reply_markup=reply_markup)

# هندلر دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("|")
    if len(data) != 3:
        await query.edit_message_text("خطا در داده‌های دریافتی.")
        return

    action, song_query, quality = data
    if action != "download":
        await query.edit_message_text("دکمه نامعتبر.")
        return

    await query.edit_message_text(f"در حال جستجو و دانلود آهنگ «{song_query}» با کیفیت {quality}...")

    try:
        # اگر کیفیت فلک خواسته شده، از yt-dlp با فرمت flac استفاده می‌کنیم
        if quality == "flac":
            ydl_opts = {
                'format': 'bestaudio[ext=flac]/bestaudio/best',
                'noplaylist': True,
                'quiet': True,
                'outtmpl': 'downloads/%(id)s.%(ext)s',
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{song_query}", download=True)
                filename = ydl.prepare_filename(info['entries'][0])
                audio_file = filename
        else:
            audio_file, _ = download_audio(song_query, quality)
        
        with open(audio_file, 'rb') as f:
            await context.bot.send_audio(chat_id=query.message.chat_id, audio=f)
        await query.edit_message_text("آهنگ ارسال شد 🎵")
    except Exception as e:
        await query.edit_message_text(f"خطا در دانلود یا ارسال آهنگ: {str(e)}")

# تابع اصلی
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("ربات شروع به کار کرد...")
    app.run_polling()

if __name__ == "__main__":
    main()
