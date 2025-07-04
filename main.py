import os
from telegram.ext import Application, CommandHandler

TOKEN = os.getenv("7568547711:AAGZX6GgV-eOmxPDdp8ccny3bvm6dB-oAQA")

async def start(update, context):
    await update.message.reply_text("سلام! ربات تستی روی Railway اجرا شده 🎉")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
