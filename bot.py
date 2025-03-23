import telebot
import instaloader
import os
import re

# توکن رباتت رو اینجا جایگذاری کن
TOKEN = "7813928188:AAEk0_77lpZEzpMZ4VMplo4_gyJK1o10ThI"
bot = telebot.TeleBot(TOKEN)


loader = instaloader.Instaloader()


USER_AGENT = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36"

loader = instaloader.Instaloader()
loader.context._default_http_header = {"User-Agent": USER_AGENT}

# ورود به اکانت تستی اینستاگرام (اختیاری، اما توصیه‌شده)
USERNAME = "your_username"
PASSWORD = "your_password"

try:
    loader.login(USERNAME, PASSWORD)
except Exception as e:
    print("❌ خطا در ورود به اینستاگرام:", e)

# ایجاد پوشه دانلود اگر وجود نداشته باشد
if not os.path.exists("downloads"):
    os.makedirs("downloads")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "سلام! لینک پست، ریلز یا نام کاربری برای استوری رو بفرست تا دانلودش کنم.")

@bot.message_handler(func=lambda message: True)
def download_instagram_content(message):
    text = message.text.strip()

    if "instagram.com/p/" in text or "instagram.com/reel/" in text:
        bot.reply_to(message, "🔄 در حال دانلود... لطفاً صبر کنید.")
        try:
            shortcode = text.split("/")[-2]  # استخراج کد پست یا ریلز
            post = instaloader.Post.from_shortcode(loader.context, shortcode)
            loader.download_post(post, target="downloads")
            send_downloaded_files(message.chat.id)
        except Exception as e:
            bot.reply_to(message, f"❌ خطا در دانلود: {e}")
            print("خطا:", e)

    elif re.match(r'^[a-zA-Z0-9_.]+$', text):  # بررسی اینکه پیام یک نام کاربری باشد
        bot.reply_to(message, "🔄 در حال دانلود استوری...")
        try:
            loader.download_profiles([text], profile_pic_only=False, fast_update=True, stories=True, target="downloads")
            send_downloaded_files(message.chat.id)
        except Exception as e:
            bot.reply_to(message, f"❌ خطا در دانلود استوری: {e}")
            print("خطا:", e)

def send_downloaded_files(chat_id):
    """ ارسال فایل‌های دانلود شده به کاربر """
    for file in os.listdir("downloads"):
        file_path = os.path.join("downloads", file)
        if file.endswith(".jpg"):
            with open(file_path, "rb") as f:
                bot.send_photo(chat_id, f)
        elif file.endswith(".mp4"):
            with open(file_path, "rb") as f:
                bot.send_video(chat_id, f)
        os.remove(file_path)  # حذف فایل پس از ارسال
    os.rmdir("downloads")  # حذف پوشه بعد از ارسال

# اجرای ربات
print("✅ ربات در حال اجراست...")
bot.polling()
