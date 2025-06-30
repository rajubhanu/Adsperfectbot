import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from html import escape
from uuid import uuid4

ADS_STORAGE_FILE = "ads_pending.txt"
CHANNELS = ["@programming_adda", "@telugu_movies_worldz", "@bmrinfotechdeals", "@TollywoodMatters", "@hotdeelss", "@hemoviess"]

def save_ad(ad):
    with open(ADS_STORAGE_FILE, "a", encoding="utf-8") as f:
        f.write(str(ad) + "\n")

async def delete_post_after_delay(bot, chat_id, message_id, delay_minutes=60):
    await asyncio.sleep(delay_minutes * 60)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
        print(f"🗑️ Deleted message from {chat_id}")
    except Exception as e:
        print(f"⚠️ Could not delete message from {chat_id}: {e}")

async def ad_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    user = msg.from_user
    ad_id = str(uuid4())
    text = msg.text or msg.caption or ""

    if not text.strip():
        await msg.reply_text("❗ Ad text is empty. Please send a valid ad with text or caption.")
        return

    escaped_text = escape(text)
    ad = {
        "id": ad_id,
        "user_id": user.id,
        "text": text,
        "photo": msg.photo[-1].file_id if msg.photo else None
    }
    save_ad(ad)

    for channel in CHANNELS:
        try:
            if ad["photo"]:
                sent_msg = await context.bot.send_photo(chat_id=channel, photo=ad["photo"], caption=text, parse_mode="HTML")
            else:
                sent_msg = await context.bot.send_message(chat_id=channel, text=text, parse_mode="HTML")

            # Schedule deletion after 60 minutes
            context.application.job_queue.run_once(lambda ctx: asyncio.create_task(delete_post_after_delay(context.bot, channel, sent_msg.message_id)), when=60*60)
        except Exception as e:
            print(f"Error posting to {channel}: {e}")

    await msg.reply_text("✅ Your ad has been posted to all channels.")