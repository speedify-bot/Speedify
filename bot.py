import logging
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from yt_dlp import YoutubeDL
import asyncio

# ✅ توکن رباتت اینجاست:
TOKEN = "8091607004:AAERzAiFaJufb4kCH-8qNq99SALJ6_fsx6Q"

# فعال‌سازی لاگ‌ها
logging.basicConfig(level=logging.INFO)

# دکمه‌های انتخاب کیفیت
quality_buttons = [
    [InlineKeyboardButton("🎧 MP3 128", callback_data="128")],
    [InlineKeyboardButton("🎧 MP3 320", callback_data="320")],
    [InlineKeyboardButton("🎼 FLAC", callback_data="flac")]
]

# ذخیره پیام‌ کاربران
user_messages = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک آهنگ یا اسمش رو بفرست 🎵")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_messages[user_id] = update.message.text
    await update.message.reply_text("🔊 کیفیت مورد نظر رو انتخاب کن:", reply_markup=InlineKeyboardMarkup(quality_buttons))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in user_messages:
        await query.edit_message_text("لینک یا اسم آهنگ رو اول بفرست.")
        return

    text = user_messages[user_id]
    quality = query.data

    msg = await query.edit_message_text("🎶 در حال پردازش آهنگ...")

    try:
        opts = {
            "format": "bestaudio",
            "outtmpl": f"{user_id}.%(ext)s",
            "quiet": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3" if quality != "flac" else "flac",
                "preferredquality": quality if quality != "flac" else "0"
            }]
        }

        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(text, download=True)
            filename = ydl.prepare_filename(info)
            audio_path = f"{user_id}.{'mp3' if quality != 'flac' else 'flac'}"

        await context.bot.send_audio(chat_id=query.message.chat_id, audio=open(audio_path, "rb"),
                                     title=info.get("title", "🎵 آهنگ"), performer=info.get("uploader", ""),
                                     duration=int(info.get("duration", 0)))

        os.remove(audio_path)

    except Exception as e:
        await msg.edit_text(f"❌ خطا در دریافت آهنگ:\n{str(e)}")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
