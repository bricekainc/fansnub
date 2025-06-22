import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import BOT_TOKEN
from supabase_client import add_user, get_all_users, search_creators, search_posts
from rss_checker import check_new_posts

# Start command with welcome message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username)
    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n\n"
        "I’ll keep you updated with Fansnub new creators and blog posts.\n\n"
        "📌 Available commands:\n"
        "/search_creator <name> – Find a creator (e.g /search_creator Fansnub) \n"
        "/search_post <keyword> – Find a blog post  (e.g /search_post deposit) "
    )

# Search creator command
async def search_creator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("❗ Usage: /search_creator <name>")
        return

    results = search_creators(query)
    if results:
        message = "\n\n".join([f"👤 {r['name']} (@{r['username']})" for r in results])
    else:
        message = "🚫 No creators found."
    await update.message.reply_text(message)

# Search post command
async def search_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("❗ Usage: /search_post <keyword>")
        return

    results = search_posts(query)
    if results:
        message = "\n\n".join([f"📝 {r['title']}\n🔗 {r['link']}" for r in results])
    else:
        message = "🚫 No blog posts found."
    await update.message.reply_text(message)

# Background task to notify users
async def notify_users():
    while True:
        new_posts = check_new_posts()
        if new_posts:
            users = get_all_users()
            for user in users:
                for title, link in new_posts:
                    try:
                        await app.bot.send_message(chat_id=user["telegram_id"], text=f"🆕 {title}\n{link}")
                    except Exception as e:
                        print(f"Failed to send to {user['telegram_id']}: {e}")
        await asyncio.sleep(600)

# App entrypoint
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search_creator", search_creator))
    app.add_handler(CommandHandler("search_post", search_post))

    # Start background task and polling
    loop = asyncio.get_event_loop()
    loop.create_task(notify_users())
    app.run_polling()
