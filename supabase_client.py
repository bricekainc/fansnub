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


def get_all_users():
    return get_users()


# ✅ Get all creators (with optional pagination)
def get_all_creators(limit=10, offset=0):
    url = f"{SUPABASE_URL}/rest/v1/creators?select=name,username,link&limit={limit}&offset={offset}"
    res = requests.get(url, headers=headers)
    return res.json() if res.status_code == 200 else []


# ✅ Get all posts (with optional pagination)
def get_all_posts(limit=10, offset=0):
    url = f"{SUPABASE_URL}/rest/v1/posts?select=title,link,tags&limit={limit}&offset={offset}"
    res = requests.get(url, headers=headers)
    return res.json() if res.status_code == 200 else []


# ✅ Case-insensitive search creators by name (with optional filter by username)
def search_creators(keyword, username_filter=None, limit=10, offset=0):
    url = f"{SUPABASE_URL}/rest/v1/creators?select=name,username,link&name=ilike.*{keyword}*&limit={limit}&offset={offset}"
    if username_filter:
        url += f"&username=eq.{username_filter}"
    res = requests.get(url, headers=headers)
    return res.json() if res.status_code == 200 else []


# ✅ Case-insensitive search blog posts by title
def search_posts(keyword, limit=10, offset=0):
    url = f"{SUPABASE_URL}/rest/v1/posts?select=title,link,tags&title=ilike.*{keyword}*&limit={limit}&offset={offset}"
    res = requests.get(url, headers=headers)
    return res.json() if res.status_code == 200 else []


# ✅ Search posts by tag (case-insensitive, assumes tags column exists and is text[])
def search_posts_by_tag(tag, limit=10, offset=0):
    url = f"{SUPABASE_URL}/rest/v1/posts?select=title,link,tags&tags=cs.%7B{tag}%7D&limit={limit}&offset={offset}"
    res = requests.get(url, headers=headers)
    return res.json() if res.status_code == 200 else []
