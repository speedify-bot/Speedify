import os
import tempfile
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import yt_dlp

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# نگهداری موقتی اطلاعات دانلود
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک SoundCloud رو بفرست تا برات دانلود کنم و کیفیت رو انتخاب کنی.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if "soundcloud.com" not in text:
        await update.message.reply_text("لطفا فقط لینک SoundCloud ارسال کن.")
        return

    msg = await update.message.reply_text("در حال بررسی کیفیت‌های موجود ... لطفا صبر کن.")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'simulate': True,
        'forceurl': True,
        'forcejson': True,
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(text, download=False)

        formats = []
        for f in info['formats']:
            # فقط صوتی ها
            if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                # بگیر فقط فرمت های mp3, m4a, flac, wav
                if f.get('ext') in ['mp3', 'm4a', 'flac', 'wav']:
                    # نرخ بیت و کیفیت
                    abr = f.get('abr') or 0
                    formats.append({
                        'format_id': f['format_id'],
                        'ext': f['ext'],
                        'abr': abr,
                        'url': f['url']
                    })

        if not formats:
            await msg.edit_text("کیفیت مناسبی پیدا نشد، مستقیماً دانلود می‌کنم.")
            user_data[update.effective_user.id] = {'url': text}
            await download_and_send(update, text, None)
            return

        # مرتب سازی کیفیت از کم به زیاد
        formats = sorted(formats, key=lambda x: x['abr'])

        # دکمه‌ها بساز
        buttons = []
        for f in formats:
            label = f"{f['abr']} kbps - {f['ext'].upper()}" if f['abr'] else f"{f['ext'].upper()}"
            buttons.append([InlineKeyboardButton(label, callback_data=f"quality|{f['format_id']}|{text}")])

        await msg.edit_text("کیفیت مورد نظرت رو انتخاب کن:", reply_markup=InlineKeyboardMarkup(buttons))

        # ذخیره موقتی
        user_data[update.effective_user.id] = {'formats': formats, 'url': text}

    except Exception as e:
        logger.error(f"Error: {e}")
        await msg.edit_text("مشکلی پیش اومد، لطفا دوباره امتحان کن.")

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split('|')
    if data[0] == 'quality':
        format_id = data[1]
        url = data[2]
        user_id = update.effective_user.id

        await query.edit_message_text("در حال دانلود و ارسال آهنگ ... لطفا صبر کن.")

        await download_and_send(update, url, format_id)

async def download_and_send(update: Update, url: str, format_id: str):
    user_id = update.effective_user.id
    temp_dir = tempfile.gettempdir()

    ydl_opts = {
        'format': format_id if format_id else 'bestaudio/best',
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }

    # اگر کاربر کیفیت خاصی انتخاب کرد و فرمت flac بود، پس پس‌پردازش رو حذف کنیم چون میخوایم flac رو مستقیم بفرستیم
    if format_id:
        # پیداکردن ext فرمت انتخابی
        user_info = user_data.get(user_id, {})
        formats = user_info.get('formats', [])
        selected_format = next((f for f in formats if f['format_id'] == format_id), None)
        if selected_format and selected_format['ext'] == 'flac':
            # حذف پس‌پردازش تبدیل به mp3
            ydl_opts.pop('postprocessors')

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # اگر تبدیل mp3 شد پس پسوند mp3 است
        if 'postprocessors' in ydl_opts:
            audio_path = os.path.splitext(filename)[0] + '.mp3'
        else:
            audio_path = filename

        with open(audio_path, 'rb') as f:
            await update.message.reply_audio(audio=InputFile(f, filename=os.path.basename(audio_path)),
                                             caption=f"🎶 {info.get('title','آهنگ')}\n🎤 {info.get('uploader','خواننده نامشخص')}")
        os.remove(audio_path)

    except Exception as e:
        logger.error(f"Download error: {e}")
        await update.message.reply_text("مشکلی در دانلود آهنگ پیش اومد!")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(callback_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
