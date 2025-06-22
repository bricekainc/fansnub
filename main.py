import os
import logging
import asyncio
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

# FastAPI app (for health check)
web_app = FastAPI()

@web_app.get("/")
def read_root():
    return {"status": "Fansnub Bot is running"}

# Logging
logging.basicConfig(level=logging.INFO)

# Constants
CREATORS_PER_PAGE = 5
POSTS_PER_PAGE = 5

# Telegram Bot Handlers

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
        "/search <keyword> – Search all content",
        reply_markup=reply_markup
    )

async def list_creators(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.split("_")[-1])
    offset = page * CREATORS_PER_PAGE

    creators = supabase_client.get_all_creators(limit=CREATORS_PER_PAGE, offset=offset)
    keyboard = [
        [InlineKeyboardButton(f"🔔 {c['name']}", url=c['link'])]
        for c in creators
    ]

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"list_creators_{page-1}"))
    if len(creators) == CREATORS_PER_PAGE:
        nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"list_creators_{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)

    await query.edit_message_text("👥 List of Creators:", reply_markup=InlineKeyboardMarkup(keyboard))

async def list_posts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.split("_")[-1])
    offset = page * POSTS_PER_PAGE

    posts = supabase_client.get_all_posts(limit=POSTS_PER_PAGE, offset=offset)
    keyboard = [
        [InlineKeyboardButton(f"📖 {p['title']}", url=p['link'])]
        for p in posts
    ]

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"list_posts_{page-1}"))
    if len(posts) == POSTS_PER_PAGE:
        nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"list_posts_{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)

    await query.edit_message_text("📰 Blog Posts:", reply_markup=InlineKeyboardMarkup(keyboard))

# Search commands

async def search_creator_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /creator <keyword>")
        return

    keyword = " ".join(context.args)
    results = supabase_client.search_creators(keyword)
    if not results:
        await update.message.reply_text("🚫 No creators found.")
    else:
        for r in results:
            await update.message.reply_text(
                f"👤 {r['name']}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔔 Subscribe", url=r['link'])]
                ])
            )

async def search_post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /post <keyword>")
        return

    keyword = " ".join(context.args)
    results = supabase_client.search_posts(keyword)
    if not results:
        await update.message.reply_text("🚫 No posts found.")
    else:
        for r in results:
            await update.message.reply_text(
                f"📰 {r['title']}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📖 Read", url=r['link'])]
                ])
            )

async def tag_search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /tag <tag>")
        return

    tag = " ".join(context.args)
    results = supabase_client.search_posts_by_tag(tag)
    if not results:
        await update.message.reply_text("🚫 No posts found for that tag.")
    else:
        for r in results:
            await update.message.reply_text(
                f"🏷️ {r['title']}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📖 Read", url=r['link'])]
                ])
            )

async def search_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /search <keyword>")
        return

    keyword = " ".join(context.args)
    creators = supabase_client.search_creators(keyword)
    posts = supabase_client.search_posts(keyword)

    if not creators and not posts:
        await update.message.reply_text("🚫 No results found.")
        return

    if creators:
        await update.message.reply_text("👥 Creators found:")
        for r in creators:
            await update.message.reply_text(
                f"👤 {r['name']}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔔 Subscribe", url=r['link'])]
                ])
            )

    if posts:
        await update.message.reply_text("📰 Posts found:")
        for r in posts:
            await update.message.reply_text(
                f"📰 {r['title']}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📖 Read", url=r['link'])]
                ])
            )

# Entry point
async def start_bot():
    app = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("creator", search_creator_command))
    app.add_handler(CommandHandler("post", search_post_command))
    app.add_handler(CommandHandler("tag", tag_search_command))
    app.add_handler(CommandHandler("search", search_all_command))

    app.add_handler(CallbackQueryHandler(list_creators, pattern=r"^list_creators_\d+$"))
    app.add_handler(CallbackQueryHandler(list_posts, pattern=r"^list_posts_\d+$"))

    await app.run_polling()

if __name__ == "__main__":
    # Launch FastAPI and Bot in asyncio loop
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())
    uvicorn.run(web_app, host="0.0.0.0", port=8000)
