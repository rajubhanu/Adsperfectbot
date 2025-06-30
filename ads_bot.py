
import os
import logging
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta

# Your bot token and channel list
BOT_TOKEN = "8027278540:AAGhpK7NOV0HPZKKlDR-QrRN1NW2LTbq7FE"
CHANNELS = ["@programming_adda", "@telugu_movies_worldz", "@bmrinfotechdeals", "@TollywoodMatters", "@hotdeelss", "@hemoviess"]

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Scheduler for auto-delete
scheduler = AsyncIOScheduler()
scheduler.start()

# Handle incoming messages with text, image, or PDF
async def handle_ad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    ad_text = message.caption or message.text or ""

    if not ad_text.strip() and not (message.document or message.photo):
        await message.reply_text("❗ Please send an ad with text, image, or PDF.")
        return

    for channel in CHANNELS:
        try:
            if message.document:
                if message.document.mime_type == "application/pdf":
                    sent = await context.bot.send_document(chat_id=channel, document=message.document.file_id, caption=ad_text)
            elif message.photo:
                sent = await context.bot.send_photo(chat_id=channel, photo=message.photo[-1].file_id, caption=ad_text)
            elif ad_text:
                sent = await context.bot.send_message(chat_id=channel, text=ad_text)
            else:
                continue

            delete_time = datetime.utcnow() + timedelta(hours=1)
            scheduler.add_job(context.bot.delete_message, DateTrigger(run_date=delete_time),
                              kwargs={'chat_id': channel, 'message_id': sent.message_id})
        except Exception as e:
            logger.error(f"Error posting to {channel}: {e}")

    await message.reply_text("✅ Your ad has been sent to all channels. It will be auto-deleted after 1 hour.")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Welcome to AdsPerfect! Send your ad with image, text or PDF.")

# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle_ad))
    logger.info("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
