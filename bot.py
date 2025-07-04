import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp

# لاگ‌ها برای بررسی ارورها
logging.basicConfig(level=logging.INFO)

# دریافت متغیرها از محیط (که در Render تعریف کردی)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# اتصال به اسپاتیفای
sp = Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

# دانلود آهنگ با کیفیت انتخاب‌شده
def download_audio(query, quality):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'flac' if quality == 'FLAC' else 'mp3',
            'preferredquality': '320' if quality == '320kbps' else '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        filename = ydl.prepare_filename(info)
        return filename.replace('.webm', f'.{"flac" if quality == "FLAC" else "mp3"}')

# ارسال کیفیت‌ها
async def ask_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    context.user_data["query"] = query

    keyboard = [
        [InlineKeyboardButton("🎧 MP3 320kbps", callback_data="320kbps")],
        [InlineKeyboardButton("🎶 MP3 192kbps", callback_data="192kbps")],
        [InlineKeyboardButton("🎵 FLAC (High)", callback_data="FLAC")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎼 لطفاً کیفیت آهنگ رو انتخاب کن:", reply_markup=reply_markup)

# واکنش به انتخاب کیفیت
async def send_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    quality = query.data
    search_query = context.user_data.get("query")

    await query.edit_message_text("🎧 در حال دریافت آهنگ...")

    # اگر لینک اسپاتیفای بود، تبدیل به نام بشه
    if "open.spotify.com" in search_query:
        try:
            track_id = search_query.split("/")[-1].split("?")[0]
            track = sp.track(track_id)
            search_query = f"{track['name']} {track['artists'][0]['name']}"
        except Exception as e:
            await query.message.reply_text("❌ خطا در پردازش لینک اسپاتیفای.")
            return

    try:
        audio_file = download_audio(f"ytsearch:{search_query}", quality)
        await query.message.reply_audio(audio=open(audio_file, "rb"), title=search_query)
        os.remove(audio_file)
    except Exception as e:
        logging.error(e)
        await query.message.reply_text("❌ خطا در دانلود آهنگ. دوباره تلاش کن.")

# استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 خوش اومدی به ربات دانلود آهنگ!\n\nفقط اسم آهنگ یا لینک اسپاتیفای رو برام بفرست.")

# اجرای ربات
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_quality))
    app.add_handler(CallbackQueryHandler(send_audio))

    app.run_polling()
