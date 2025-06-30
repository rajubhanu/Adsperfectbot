import logging
import os
from telegram import Update, InputMediaPhoto, InputFile
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from html import escape
from datetime import datetime, timedelta
import pytz

BOT_TOKEN = "8027278540:AAGhpK7NOV0HPZKKlDR-QrRN1NW2LTbq7FE"
CHANNELS = ["@programming_adda", "@telugu_movies_worldz", "@bmrinfotechdeals", "@TollywoodMatters", "@hotdeelss", "@hemoviess"]
ADMIN_ID = 1367831694
ADS_FILE = "ads.txt"
timezone = pytz.timezone("Asia/Kolkata")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ads = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Welcome to AdsPerfect!

📤 Send your ad with image, text or PDF.
📌 It will be auto-posted to all our channels.")

def save_ad(ad):
    with open(ADS_FILE, "a", encoding="utf-8") as f:
        f.write(str(ad) + "\n")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    text = msg.caption or msg.text or ""
    if not text.strip():
        await msg.reply_text("❌ Please send some text or caption.")
        return

    text = escape(text)
    media = None
    ad = {"text": text, "time": datetime.now(timezone).isoformat()}

    if msg.document:
        ad["document"] = msg.document.file_id
    elif msg.photo:
        ad["photo"] = msg.photo[-1].file_id

    save_ad(ad)
    ads.append(ad)

    for ch in CHANNELS:
        try:
            if "photo" in ad:
                await context.bot.send_photo(ch, ad["photo"], caption=text, parse_mode="HTML")
            elif "document" in ad:
                await context.bot.send_document(ch, ad["document"], caption=text, parse_mode="HTML")
            else:
                await context.bot.send_message(ch, text, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Error posting to {ch}: {e}")

    await msg.reply_text("✅ Ad posted to all channels!")

def auto_delete_ads():
    global ads
    now = datetime.now(timezone)
    ads = [ad for ad in ads if (now - datetime.fromisoformat(ad['time'])).total_seconds() < 3600]
    with open(ADS_FILE, "w", encoding="utf-8") as f:
        for ad in ads:
            f.write(str(ad) + "\n")
    logger.info("🧹 Old ads cleaned.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle_message))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(auto_delete_ads, "interval", hours=1)
    scheduler.start()

    logger.info("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
