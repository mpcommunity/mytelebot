import google.generativeai as gg
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import os

# 🔐 API Keyها (اینجا کلیدهایت رو قرار بده)
GEMINI_API_KEY = "AIzaSyBhbiOFG9-7z8ELNqizVWeoJnZmONKgjxY"
BOT_TOKEN = "8416210407:AAGQdcO2D2x432JqBg8OJofzUt13wWQY1BY"

# 🤖 تنظیم Gemini
gg.configure(api_key=GEMINI_API_KEY)
model = gg.GenerativeModel('gemini-1.5-flash')
chat = model.start_chat()

# 📦 حافظه موقت کاربران
user_data = {}

# ✅ /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لطفاً فایل نظرات (فرمت txt) رو بفرست.")

# 📄 دریافت فایل txt
async def handle_txt_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    document = update.message.document

    if document.mime_type != "text/plain":
        await update.message.reply_text("فقط فایل txt ارسال کن لطفاً.")
        return

    file = await document.get_file()
    file_path = f"/tmp/{user_id}_opinions.txt"
    await file.download_to_drive(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        user_data[user_id] = {"content": content}
        await update.message.reply_text("✅ فایل دریافت شد. حالا نام محصول رو وارد کن.")
    except Exception as e:
        print("❌ خطا در خوندن فایل:", e)
        await update.message.reply_text("مشکلی در پردازش فایل به‌وجود اومد.")

# 📝 دریافت نام محصول
async def handle_product_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    product_name = update.message.text.strip()

    if user_id not in user_data or "content" not in user_data[user_id]:
        await update.message.reply_text("❗️لطفاً اول فایل نظرات رو بفرست.")
        return

    content = user_data[user_id]["content"]

    # 📌 ساخت سوال برای Gemini
    question = (
        f"متنی که در ادامه برات می‌فرستم نظرات مردم در مورد کالای «{product_name}» در دیجی‌کالاست.\n"
        "لطفا نظرات را خلاصه‌سازی کن و جمع‌بندی نهایی را برام بفرست.\n"
        "فقط دیدگاه‌های مردم رو جمع‌بندی کن، نظر خودت رو وارد نکن. ممنون.\n\n"
        + content
    )

    try:
        response = chat.send_message(question)
        await update.message.reply_text("🤖 پاسخ هوش مصنوعی:\n\n" + response.text)
        user_data.pop(user_id)  # پاک کردن داده بعد از جواب
    except Exception as e:
        print("❌ خطا در ارتباط با Gemini:", e)
        await update.message.reply_text("مشکلی در ارتباط با هوش مصنوعی پیش اومد.")

# 🆘 /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 راهنما:\n"
        "1- فایل txt نظرات رو بفرست\n"
        "2- بعدش نام محصول رو بنویس\n"
        "3- منتظر خلاصه‌سازی باش 🤖"
    )

# 🏁 اجرا
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.Document.MimeType("text/plain"), handle_txt_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_product_name))

    print("✅ ربات فعال شد.")
    app.run_polling()

if __name__ == "__main__":
    main()
