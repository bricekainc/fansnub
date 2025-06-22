import os
import requests

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

# ✅ Required for notify_users()
def get_all_users():
    return get_users()

# 🔍 Search creators by name (case-insensitive)
def search_creators(keyword):
    params = {
        "name": f"ilike.*{keyword}*"
    }
    res = requests.get(f"{SUPABASE_URL}/rest/v1/creators", headers=headers, params=params)
    return res.json() if res.status_code == 200 else []

# 🔍 Search blog posts by title (case-insensitive)
def search_posts(keyword):
    params = {
        "title": f"ilike.*{keyword}*"
    }
    res = requests.get(f"{SUPABASE_URL}/rest/v1/posts", headers=headers, params=params)
    return res.json() if res.status_code == 200 else []
