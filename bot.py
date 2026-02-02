import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# التوكن الخاص بك
BOT_TOKEN = "1448950819:AAG1a1IrYm7VNAI-vLR2dw_kXlhTZOKGEwc"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت يعمل بنجاح الآن!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # بناء التطبيق بأحدث طريقة متوافقة مع السيرفر
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    print("🚀 جاري تشغيل البوت...")
    application.run_polling()
