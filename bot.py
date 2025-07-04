import os import asyncio from telegram import Update from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters import spotipy from spotipy.oauth2 import SpotifyClientCredentials import nest_asyncio

==================== راه‌اندازی سرور فیک برای Render ====================

Render نیاز به پورت باز دارد، پس یک سرور ساده روی یک پورت ران می‌کنیم تا خطا ندهد

import http.server import socketserver import threading

def fake_server(): PORT = int(os.getenv("PORT", 10000)) Handler = http.server.SimpleHTTPRequestHandler with socketserver.TCPServer(("", PORT), Handler) as httpd: print(f"Fake server running on port {PORT}") httpd.serve_forever()

اجرای سرور فیک در ترد جداگانه

threading.Thread(target=fake_server).start()

==================== گرفتن اطلاعات مهم از متغیرهای محیطی ====================

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID") SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET") TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

==================== اتصال به Spotify API ====================

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials( client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET ))

==================== دستور /start ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text( "🎧 سلام! به ربات HeadzBeats خوش اومدی!\n" "لطفاً لینک یک آهنگ از اسپاتیفای برام بفرست، تا مشخصاتشو برات دربیارم." )

==================== پاسخ‌دهی به پیام‌های کاربر ====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): text = update.message.text

if "open.spotify.com/track" in text:
    try:
        track_id = text.split("track/")[1].split("?")[0]
        track = sp.track(track_id)
        name = track.get("name", "نامشخص")
        artists = ", ".join([artist.get("name", "؟") for artist in track.get("artists", [])])
        album = track.get("album", {}).get("name", "نامشخص")
        preview = track.get("preview_url") or "⛔️ این آهنگ پیش‌نمایش (Preview) نداره."

        response = (
            f"🎶 آهنگ: {name}\n"
            f"🎤 خواننده: {artists}\n"
            f"💿 آلبوم: {album}\n"
            f"🔗 پیش‌نمایش: {preview}"
        )
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطا در دریافت اطلاعات آهنگ:\n{str(e)}")
else:
    await update.message.reply_text("❗️ لطفاً فقط لینک مستقیم یک آهنگ از اسپاتیفای بفرست.")

==================== اجرای ربات ====================

async def main(): app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# ثبت دستور /start
app.add_handler(CommandHandler("start", start))

# ثبت پیام‌های متنی (غیر از کامند)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

await app.run_polling()

==================== اجرای ایمن Asyncio روی Render ====================

nest_asyncio.apply() asyncio.get_event_loop().run_until_complete(main())

