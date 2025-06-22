import os
import logging
import threading
from fastapi import FastAPI
import uvicorn

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import supabase_client
from config import BOT_TOKEN

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CREATORS_PER_PAGE = 5
POSTS_PER_PAGE = 5

# FastAPI dummy app
web_app = FastAPI()

@web_app.get("/")
def read_root():
    return {"status": "Fansnub Bot is running"}

# Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📜 Show All Creators", callback_data="list_creators_0")],
        [InlineKeyboardButton("📰 Show All Posts", callback_data="list_posts_0")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Welcome to the Fansnub Bot!\n"
        "Browse creators and read blog posts.\n\n"
        "📌 Available commands:\n"
        "/creator <name> – Find a creator\n"
        "/post <keyword> – Find a blog post\n"
        "/tag <tag> – Search posts by tag\n"
        "/search <keyword> – Search creators and posts",
        reply_markup=reply_markup
    )

# Callback handlers...
# (KEEP all your other handlers like list_creators, list_posts, etc unchanged)

# --- Telegram Bot Runner ---
def run_bot():
    try:
        logger.info("🚀 Starting Telegram bot...")
        application = ApplicationBuilder().token(BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("creator", search_creator_command))
        application.add_handler(CommandHandler("post", search_post_command))
        application.add_handler(CommandHandler("tag", tag_search_command))
        application.add_handler(CommandHandler("search", search_all_command))

        application.add_handler(CallbackQueryHandler(list_creators, pattern=r"^list_creators_\d+$"))
        application.add_handler(CallbackQueryHandler(list_posts, pattern=r"^list_posts_\d+$"))

        application.run_polling()
    except Exception as e:
        logger.error(f"❌ Bot failed to start: {e}")

# --- Start everything ---
if __name__ == "__main__":
    logger.info("🔧 Launching app...")

    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    uvicorn.run("main:web_app", host="0.0.0.0", port=8000)
