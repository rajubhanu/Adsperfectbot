import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from html import escape
from datetime import datetime, timedelta
from datetime import datetimeAdd commentMore actions
import pytz
import os
BOT_TOKEN = "8027278540:AAH91oOZa8RxmRnx_mNIsIMFcjXoCfbCceE"
CHANNELS = [
    "@programming_adda", "@telugu_movies_worldz", "@bmrinfotechdeals",
    "@TollywoodMatters", "@hotdeelss", "@hemoviess"
]
timezone = pytz.timezone("Asia/Kolkata")
ADS_FILE = "ads.txt"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ads = []
ADMIN_ID = 1367831694  # ✅ Your Telegram user ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⚠️ Sorry, you're not authorized to use this bot.")
        return

    await update.message.reply_text("🤖 Welcome, Admin! Send your ad with text/image or document.")


def save_ad(ad):
    with open(ADS_FILE, "a", encoding="utf-8") as f:
        f.write(str(ad) + "\n")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await msg.reply_text("❌ Only the admin can post ads.")
        return

    # Rest of your ad handling logic below...


    text = msg.caption or msg.text or ""
    if not text.strip():
        await msg.reply_text("❌ Please include some text.")
        return

    text = escape(text)
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
    ads = [ad for ad in ads if (now - datetime.fromisoformat(ad["time"])).total_seconds() < 3600]
    with open(ADS_FILE, "w", encoding="utf-8") as f:
        for ad in ads:
            f.write(str(ad) + "\n")
    logger.info("🧹 Old ads cleaned.")

async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_message))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(auto_delete_ads, "interval", hours=1)
    scheduler.start()

    logger.info("Bot started...")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
