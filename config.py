import os
from dotenv import load_dotenv

load_dotenv()

# Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is missing from environment variables.")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ SUPABASE_URL or SUPABASE_KEY is missing from environment variables.")

# RSS Feeds (comma-separated)
FEED_URLS = os.getenv("FEED_URLS", "").split(",")
FEED_URLS = [url.strip() for url in FEED_URLS if url.strip()]  # Clean empty entries

if not FEED_URLS:
    raise ValueError("❌ FEED_URLS is empty. Provide at least one RSS feed URL.")
