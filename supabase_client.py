import os
import requests
import feedparser

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

def add_user(telegram_id, username):
    data = {
        "telegram_id": telegram_id,
        "username": username,
    }
    res = requests.post(f"{SUPABASE_URL}/rest/v1/users", json=data, headers=headers)
    return res.status_code == 201

def get_users():
    res = requests.get(f"{SUPABASE_URL}/rest/v1/users", headers=headers)
    return res.json() if res.status_code == 200 else []

def get_all_users():
    return get_users()

# ✅ Get all creators (from RSS)
def get_all_creators(limit=None, offset=0):
    url = "https://fansnub.com/rss/creators/feed/"
    feed = feedparser.parse(url)
    entries = feed.entries[offset:]
    if limit is not None:
        entries = entries[:limit]
    return [{"name": e.title, "link": e.link} for e in entries]

# 🔍 Search creators by name (case-insensitive, RSS-based), with pagination
def search_creators(keyword, limit=None, offset=0):
    url = "https://fansnub.com/rss/creators/feed/"
    feed = feedparser.parse(url)
    lkey = keyword.casefold()
    results = [ 
        {"name": e.title, "link": e.link}
        for e in feed.entries
        if lkey in e.title.casefold()
    ]
    return results[offset:offset + limit] if limit else results

# 🔍 Filter creators by exact username
def filter_creator_by_username(username):
    url = "https://fansnub.com/rss/creators/feed/"
    feed = feedparser.parse(url)
    uname = username.casefold()
    results = [
        {"name": e.title, "link": e.link}
        for e in feed.entries
        if uname in e.link.casefold()  # Assuming link contains username
    ]
    return results

# ✅ Get all posts (with pagination)
def get_all_posts(limit=None, offset=0):
    url = f"{SUPABASE_URL}/rest/v1/posts?select=title,link&order=created_at.desc&limit=1000"
    res = requests.get(url, headers=headers)
    posts = res.json() if res.status_code == 200 else []
    posts = posts[offset:]
    if limit:
        posts = posts[:limit]
    return posts

# 🔍 Search blog posts by title (case-insensitive), with pagination
def search_posts(keyword, limit=None, offset=0):
    url = f"{SUPABASE_URL}/rest/v1/posts?select=title,link&title=ilike.*{keyword}*"
    res = requests.get(url, headers=headers)
    posts = res.json() if res.status_code == 200 else []
    posts = posts[offset:]
    if limit:
        posts = posts[:limit]
    return posts

# 🔍 Search blog posts by tag
def search_posts_by_tag(tag, limit=None, offset=0):
    url = f"{SUPABASE_URL}/rest/v1/posts?select=title,link,tags&tags=ilike.*{tag}*"
    res = requests.get(url, headers=headers)
    posts = res.json() if res.status_code == 200 else []
    posts = posts[offset:]
    if limit:
        posts = posts[:limit]
    return posts
