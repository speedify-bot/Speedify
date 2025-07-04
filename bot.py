import os import asyncio from telegram import Update from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters import spotipy from spotipy.oauth2 import SpotifyClientCredentials

سرور فیک برای Render که خطای پورت نده

import http.server import socketserver import threading

def fake_server(): PORT = int(os.getenv("PORT", 10000)) Handler = http.server.SimpleHTTPRequestHandler with socketserver.TCPServer(("", PORT), Handler) as httpd: print(f"Fake server running on port {PORT}") httpd.serve_forever()

اجرای سرور فیک در یک ترد جداگانه

threading.Thread(target=fake_server).start()

گرفتن اطلاعات محیطی از Render

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID") SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET") TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

اتصال به API اسپاتیفای

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials( client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET ))

دستور /start

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("🎵 سلام! لینک آهنگ اسپاتیفای رو بفرست تا مشخصاتشو برات دربیارم.")

بررسی لینک‌های اسپاتیفای و پاسخ‌دهی

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): text = update.message.text if "open.spotify.com/track" in text: try: track_id = text.split("track/")[1].split("?")[0] track = sp.track(track_id) name = track["name"] artists = ", ".join([artist["name"] for artist in track["artists"]]) album = track["album"]["name"] preview = track["preview_url"] or "🎧 این آهنگ پریویو نداره."

response = f"🎶 {name} - {artists}\n💿 آلبوم: {album}\n🔗 پیش‌نمایش: {preview}"
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"⛔️ نتونستم آهنگو پیدا کنم.\nخطا: {str(e)}")
else:
    await update.message.reply_text("❗️ لطفاً لینک مستقیم یک ترک از اسپاتیفای بفرست.")

اجرای اصلی ربات

async def main(): app = ApplicationBuilder().token(TELEGRAM_TOKEN).build() app.add_handler(CommandHandler("start", start)) app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)) await app.run_polling()

جلوگیری از ارور asyncio در محیط‌هایی مثل Render

import nest_asyncio nest_asyncio.apply()

اجرای async main()

asyncio.get_event_loop().run_until_complete(main())

