import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import BOT_TOKEN
from supabase_client import add_user, get_all_users
from rss_checker import check_new_posts

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username)
    await update.message.reply_text(f"Welcome {user.first_name}! You’ll get updates here.")

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
        await asyncio.sleep(600)  # every 10 minutes

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    loop = asyncio.get_event_loop()
    loop.create_task(notify_users())
    app.run_polling()
