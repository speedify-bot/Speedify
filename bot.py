import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import nest_asyncio
import http.server
import socketserver
import threading

# اجرای یک سرور ساده برای Render (الزام پورت‌بایندینگ)
def fake_server():
    PORT = int(os.getenv("PORT", 10000))
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Fake server running on port {PORT}")
        httpd.serve_forever()

threading.Thread(target=fake_server, daemon=True).start()

# دریافت متغیرهای محیطی
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# راه‌اندازی کلاینت اسپاتیفای
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎧 سلام!\n"
        "ربات HeadzBeats آماده‌ست تا اطلاعات آهنگ‌های اسپاتیفای رو بهت بده.\n"
        "کافیه لینک مستقیم یه آهنگ اسپاتیفای برام بفرستی."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if "open.spotify.com/track" in text:
        try:
            track_id = text.split("track/")[1].split("?")[0]
            track = sp.track(track_id)

            name = track.get("name", "نامشخص")
            artists = ", ".join([artist.get("name", "?") for artist in track.get("artists", [])])
            album = track.get("album", {}).get("name", "نامشخص")
            duration_ms = track.get("duration_ms", 0)
            duration_min = duration_ms // 60000
            duration_sec = (duration_ms % 60000) // 1000
            preview_url = track.get("preview_url") or "⛔️ پیش‌نمایش موجود نیست."

            message = (
                f"🎶 **آهنگ:** {name}\n"
                f"🎤 **خواننده:** {artists}\n"
                f"💿 **آلبوم:** {album}\n"
                f"⏱️ **مدت زمان:** {duration_min} دقیقه و {duration_sec} ثانیه\n"
                f"🔗 **پیش‌نمایش:** {preview_url}"
            )

            await update.message.reply_markdown(message)
        except Exception as e:
            await update.message.reply_text(f"⚠️ خطا در دریافت اطلاعات آهنگ:\n{e}")
    else:
        await update.message.reply_text("❗ لطفاً فقط لینک مستقیم آهنگ اسپاتیفای ارسال کن.")

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.run_polling()

nest_asyncio.apply()
asyncio.get_event_loop().run_until_complete(main())
