#!/bin/bash

# به‌روزرسانی مخازن بسته‌ها
apt-get update -y

# نصب ffmpeg برای تبدیل ویدئو به صوت
apt-get install -y ffmpeg

# اطمینان از نصب پایتون3 و pip (اگر سیستم هدف نسخه‌های قدیمی داشته باشه)
apt-get install -y python3 python3-pip

# به‌روزرسانی pip
pip3 install --upgrade pip

# نصب poetry اگر بخوای (اختیاری)
// curl -sSL https://install.python-poetry.org | python3 -

# (اگر رندر نیاز داشت به اجرای دستورات بیشتر اینجا اضافه کن)

echo "Build script completed successfully."
