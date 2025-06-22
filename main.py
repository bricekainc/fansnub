import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, CommandHandler, CallbackQueryHandler,
                          ContextTypes)
from config import BOT_TOKEN
from supabase_client import add_user, get_all_users, search_creators, search_posts
from rss_checker import check_new_posts

RESULTS_PER_PAGE = 3

# Start command with welcome message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username)
    await update.message.reply_text(
        f"\U0001F44B Welcome {user.first_name}!
\n"
        "I’ll keep you updated with Fansnub new creators and blog posts.\n\n"
        "📌 Available commands:\n"
        "/search_creator <name> – Find a creator (e.g. /search_creator Fansnub)\n"
        "/search_post <keyword> – Find a blog post (e.g. /search_post deposit)\n"
        "/search <keyword> – Search creators *and* blog posts together"
    )

# Paginate search results
async def paginate_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split('|')
    search_type, page, keyword = data[0], int(data[1]), data[2]

    if search_type == 'creators':
        results = search_creators(keyword)
        label = "👤 *Creators Found:*"
        format_fn = lambda c: InlineKeyboardButton(
            text=f"{c['name']} (@{c['username']})", url=c.get("link", "") or "https://fansnub.com")
    else:
        results = search_posts(keyword)
        label = "📝 *Blog Posts Found:*"
        format_fn = lambda p: InlineKeyboardButton(text=p['title'], url=p['link'])

    start_idx = page * RESULTS_PER_PAGE
    paginated = results[start_idx:start_idx + RESULTS_PER_PAGE]

    if not paginated:
        await query.edit_message_text("No more results.")
        return

    keyboard = [[format_fn(r)] for r in paginated]
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"{search_type}|{page-1}|{keyword}"))
    if start_idx + RESULTS_PER_PAGE < len(results):
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"{search_type}|{page+1}|{keyword}"))
    if nav_buttons:
        keyboard.append(nav_buttons)

    await query.edit_message_text(
        label,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Combined search command
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Usage: /search <keyword>")
        return

    keyword = " ".join(context.args)
    creators = search_creators(keyword)
    posts = search_posts(keyword)

    if not creators and not posts:
        await update.message.reply_text("🚫 No results found.")
        return

    if creators:
        await update.message.reply_text(
            "👤 *Creators Found:*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("View Results", callback_data=f"creators|0|{keyword}")]
            ])
        )

    if posts:
        await update.message.reply_text(
            "📝 *Blog Posts Found:*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("View Results", callback_data=f"posts|0|{keyword}")]
            ])
        )

# Notify users of new posts
async def notify_users():
    while True:
        new_posts = check_new_posts()
        if new_posts:
            users = get_all_users()
            for user in users:
                for title, link in new_posts:
                    try:
                        await app.bot.send_message(
                            chat_id=user["telegram_id"],
                            text=f"🆕 {title}\n{link}"
                        )
                    except Exception as e:
                        print(f"Failed to send to {user['telegram_id']}: {e}")
        await asyncio.sleep(600)

# Entrypoint
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CallbackQueryHandler(paginate_results))

    loop = asyncio.get_event_loop()
    loop.create_task(notify_users())
    app.run_polling()
