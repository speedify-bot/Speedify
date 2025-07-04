import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import asyncio

# فقط برای فریب Render :)
import http.server
import socketserver
import threading

def fake_server():
    PORT = int(os.getenv("PORT", 10000))
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving dummy HTTP on port {PORT}")
        httpd.serve_forever()

threading.Thread(target=fake_server).start()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک اسپاتیفای رو بفرست تا آهنگ رو برات بفرستم.")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text(f"دریافت لینک: {url}\n(دانلود هنوز فعال نشده)")

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("download", download))
    await app.run_polling()

asyncio.run(main())
