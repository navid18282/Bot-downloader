import telebot
import instaloader
import os
import re
from flask import Flask
import threading

# 🔹 راه‌اندازی سرور Flask برای جلوگیری از خاموش شدن در Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

# 🔹 توکن ربات تلگرام
TOKEN = "7627236492:AAGspDDGfS5MMIHnjdjNscu27rl0Ik9DNh0"
bot = telebot.TeleBot(TOKEN)

# 🔹 مقداردهی Instaloader
loader = instaloader.Instaloader()

# 🔹 ورود به حساب اینستاگرام (ذخیره نشست)
USERNAME = "naavid1386"
PASSWORD = "n4061748122"

try:
    loader.load_session_from_file(USERNAME)
    print("✅ نشست اینستاگرام بارگذاری شد.")
except FileNotFoundError:
    print("🔑 نشست یافت نشد، ورود با رمز عبور...")
    loader.login(USERNAME, PASSWORD)
    loader.save_session_to_file()
    print("✅ ورود موفقیت‌آمیز به اینستاگرام!")

# 🔹 ایجاد پوشه دانلود اگر وجود نداشته باشد
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# ✅ دستور /start و /help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "سلام! لینک پست، ریلز یا نام کاربری برای استوری رو بفرست تا دانلودش کنم.")

# ✅ پردازش لینک‌های اینستاگرام
@bot.message_handler(func=lambda message: True)
def download_instagram_content(message):
    text = message.text.strip()

    if "instagram.com/p/" in text or "instagram.com/reel/" in text or "instagram.com/tv/" in text:
        bot.reply_to(message, "🔄 در حال دانلود... لطفاً صبر کنید.")
        try:
            shortcode = text.split("/")[-2]
            L = instaloader.Instaloader()
            L.load_session_from_file(USERNAME)
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            L.download_post(post, target="downloads")
            send_downloaded_files(message.chat.id)
        except Exception as e:
            bot.reply_to(message, f"❌ خطا در دانلود: {e}")
            print("خطا:", e)

    elif re.match(r'^[a-zA-Z0-9_.]+$', text):
        bot.reply_to(message, "🔄 در حال دانلود استوری...")
        try:
            L = instaloader.Instaloader()
            L.load_session_from_file(USERNAME)
            L.download_profiles([text], profile_pic_only=False, fast_update=True, stories=True, target="downloads")
            send_downloaded_files(message.chat.id)
        except Exception as e:
            bot.reply_to(message, f"❌ خطا در دانلود استوری: {e}")
            print("خطا:", e)

# ✅ ارسال فایل‌های دانلود شده
def send_downloaded_files(chat_id):
    """ ارسال فایل‌های دانلود شده به کاربر """
    files = os.listdir("downloads")
    if not files:
        bot.send_message(chat_id, "❌ هیچ فایلی برای ارسال یافت نشد!")
        return

    for file in files:
        file_path = os.path.join("downloads", file)
        try:
            with open(file_path, "rb") as f:
                if file.endswith(".jpg") or file.endswith(".png"):
                    bot.send_photo(chat_id, f)
                elif file.endswith(".mp4"):
                    bot.send_video(chat_id, f)
        except Exception as e:
            bot.send_message(chat_id, f"❌ خطا در ارسال فایل: {e}")
            print("خطا در ارسال:", e)
        finally:
            os.remove(file_path)  # حذف فایل پس از ارسال

    os.rmdir("downloads")  # حذف پوشه بعد از ارسال
    os.makedirs("downloads")  # ایجاد مجدد پوشه

# ✅ اجرای ربات
print("✅ ربات در حال اجراست...")
bot.polling()
