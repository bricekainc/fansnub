import os
import logging
import feedparser
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables
load_dotenv()  # requires python-dotenv
BOT_TOKEN = os.getenv("BOT_TOKEN")
FEED_SITE = os.getenv("FEED_SITE")
FEED_CREATORS = os.getenv("FEED_CREATORS")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

WELCOME_MSG = (
    "👋 *Welcome to FansnubBot (@fansnubot)!*\n\n"
    "Send me a creator's name or keyword, and I'll search both:\n"
    "– Site-wide posts\n"
    "– Verified creators\n\n"
    "_Example: Lana, Riley, Mohamed_\n"
    "[Browse creators](https://fansnub.com/creators/)"
)

def fetch_feeds():
    items = []
    for url in (FEED_SITE, FEED_CREATORS):
        if url:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                items.append((entry.title, entry.link))
    return items

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MSG, parse_mode="Markdown")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.lower().strip()
    results = []
    for title, link in fetch_feeds():
        if query in title.lower():
            results.append(f"🔗 [{title}]({link})")

    if results:
        await update.message.reply_text("\n".join(results), parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ No matches found. Try another name.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
    app.run_polling()

if __name__ == "__main__":
    main()
