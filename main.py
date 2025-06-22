import os
import logging
from fastapi import FastAPI
import asyncio

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

# FastAPI app
web_app = FastAPI()

@web_app.get("/")
def read_root():
    return {"status": "Fansnub Bot is running"}

# Telegram handlers
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

# Other handlers (same as before — keep yours)

# Start bot inside FastAPI startup event
@web_app.on_event("startup")
async def start_bot():
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

        asyncio.create_task(application.run_polling())
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
