import os
import logging
import asyncio
import random
from fastapi import FastAPI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

import rss_checker
from supabase_client import get_all_users
from config import BOT_TOKEN

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI App ---
web_app = FastAPI()

# --- Constants ---
CREATORS_PER_PAGE = 5
POSTS_PER_PAGE = 5
BOT = Bot(token=BOT_TOKEN)

# --- State ---
awaiting_search_input = set()


@web_app.get("/")
def read_root():
    return {"status": "Fansnub Bot is running"}


# --- Telegram Bot Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌟 Show Today's Featured Creator", callback_data="featured_creator")],
        [InlineKeyboardButton("📰 Show All Posts", callback_data="list_posts_0")],
        [InlineKeyboardButton("🔍 Search Fansnub", callback_data="search_start")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Welcome to the Fansnub Bot!\n"
        "Browse creators and read blog posts.\n\n"
        "📌 Available commands:\n"
        "/post <keyword> – Find a blog post\n"
        "/search <keyword> – Hunt creators & posts\n",
        reply_markup=reply_markup
    )


async def show_featured_creator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    creators = rss_checker.get_all_creators(limit=1000)
    if not creators:
        await query.edit_message_text("🚫 No creators available.")
        return

    featured = random.choice(creators)
    await query.edit_message_text(
        f"🌟 Today's Featured Creator:\n\n👤 {featured['name']}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔔 Subscribe", url=featured['link'])],
            [InlineKeyboardButton("🔄 Show Another", callback_data="featured_creator")]
        ])
    )


async def list_posts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.split("_")[-1])
    offset = page * POSTS_PER_PAGE
    posts = rss_checker.get_all_posts(limit=POSTS_PER_PAGE, offset=offset)

    if not posts:
        await query.edit_message_text("🚫 No results found. Try again. Use /search <keyword>")
        return

    keyboard = [[InlineKeyboardButton(f"📖 {p['title']}", url=p['link'])] for p in posts]
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"list_posts_{page - 1}"))
    if len(posts) == POSTS_PER_PAGE:
        nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"list_posts_{page + 1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)

    await query.edit_message_text("📰 Blog Posts:", reply_markup=InlineKeyboardMarkup(keyboard))


async def initiate_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    awaiting_search_input.add(user_id)
    await query.message.reply_text("🔍 What would you like to search for? Type your keyword below:", reply_markup=ReplyKeyboardRemove())


async def handle_search_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in awaiting_search_input:
        return

    awaiting_search_input.discard(user_id)
    keyword = update.message.text.strip()

    creators = rss_checker.search_creators(keyword)
    posts = rss_checker.search_posts(keyword)

    if not creators and not posts:
        await update.message.reply_text(
            f"🚫 No results found for '{keyword}'.\n\n"
            "🧭 You can try searching directly on https://fansnub.com or contact support at https://support.briceka.com"
        )
        return

    if creators:
        await update.message.reply_text("👥 Creators found:")
        for r in creators:
            await update.message.reply_text(
                f"👤 {r['name']}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔔 Subscribe", url=r['link'])]])
            )

    if posts:
        await update.message.reply_text("🧭 Posts found:")
        for r in posts:
            await update.message.reply_text(
                f"📰 {r['title']}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📖 Read", url=r['link'])]])
            )


# --- Background Task: Notify all users of new RSS entries ---
async def notify_users_of_new_posts():
    while True:
        new_entries = rss_checker.check_new_posts()
        if new_entries:
            users = get_all_users()
            for title, link in new_entries:
                for user in users:
                    try:
                        await BOT.send_message(chat_id=user['telegram_id'], text=f"🆕 New post: {title}\n{link}")
                    except Exception as e:
                        logger.warning(f"❌ Failed to message {user['telegram_id']}: {e}")
        await asyncio.sleep(300)  # 5 minutes


# --- Start bot on FastAPI startup ---
@web_app.on_event("startup")
async def start_bot():
    try:
        logger.info("🚀 Starting Telegram bot...")

        rss_checker.refresh_feed_cache()

        app = ApplicationBuilder().token(BOT_TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("search", handle_search_input))  # fallback for /search
        app.add_handler(CallbackQueryHandler(show_featured_creator, pattern=r"^featured_creator$"))
        app.add_handler(CallbackQueryHandler(list_posts, pattern=r"^list_posts_\d+$"))
        app.add_handler(CallbackQueryHandler(initiate_search, pattern=r"^search_start$"))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_search_input))

        await app.initialize()
        await app.start()
        await app.updater.start_polling()

        asyncio.create_task(notify_users_of_new_posts())
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")


# --- Start FastAPI server ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(web_app, host="0.0.0.0", port=8000)
