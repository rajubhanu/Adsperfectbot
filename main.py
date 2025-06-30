import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.ad_submission import ad_submission

BOT_TOKEN = "8027278540:AAGhpK7NOV0HPZKKlDR-QrRN1NW2LTbq7FE"

logging.basicConfig(level=logging.INFO)
scheduler = AsyncIOScheduler()
scheduler.start()

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, ad_submission))

print("Bot started...")
app.run_polling()