import os
import logging
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CallbackQueryHandler, filters
from youtubesearchpython import VideosSearch
import yt_dlp

# فعال‌سازی لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# توکن واقعی شما از BotFather
TOKEN = "8091607004:AAERzAiFaJufb4kCH-8qNq99SALJ6_fsx6Q"

# جستجوی آهنگ در یوتیوب
async def search_youtube(query):
    search = VideosSearch(query, limit=1)
    result = search.result()['result'][0]
    return result['title'], result['link'], result['thumbnails'][0]['url'], result['duration']

# دانلود آهنگ با کیفیت دلخواه
def download_audio(url, filename="song", quality="mp3"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{filename}.{quality}',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if quality == 'mp3' else [],
        'postprocessors_args': ['-acodec', 'flac'] if quality == 'flac' else []
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return f"{filename}.{quality}"

# پاسخ به پیام کاربر
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    title, link, thumbnail, duration = await search_youtube(query)
    context.user_data['track_info'] = {"title": title, "link": link}
    keyboard = [[
        InlineKeyboardButton("🎧 MP3", callback_data="mp3"),
        InlineKeyboardButton("💽 FLAC", callback_data="flac")
    ]]
    await update.message.reply_photo(
        photo=thumbnail,
        caption=f"🎵 *{title}*\n⏱️ مدت زمان: {duration}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# پاسخ به انتخاب فرمت
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    track = context.user_data.get("track_info")
    if not track:
        await query.edit_message_text("❌ خطا در دریافت اطلاعات آهنگ.")
        return

    await query.edit_message_caption(caption=f"⬇️ درحال دانلود {choice.upper()}... لطفاً صبر کنید.")
    filename = download_audio(track['link'], filename="song", quality=choice)
    with open(filename, 'rb') as audio:
        if choice == 'mp3':
            await query.message.reply_audio(audio=audio, title=track['title'], caption="🎧 Powered by SpeedHeadz")
        else:
            await query.message.reply_document(document=audio, filename=f"{track['title']}.flac", caption="🎧 Powered by SpeedHeadz")
    os.remove(filename)

# راه‌اندازی ربات
async def main():
    import nest_asyncio
    nest_asyncio.apply()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
