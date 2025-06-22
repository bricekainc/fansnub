import os
import requests

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# Add a new Telegram user to Supabase (if not already present)
def add_user(telegram_id, username):
    data = {
        "telegram_id": telegram_id,
        "username": username,
    }
    # Prevent duplicates by checking first
    existing = requests.get(
        f"{SUPABASE_URL}/rest/v1/users?telegram_id=eq.{telegram_id}",
        headers=headers,
    )
    if existing.status_code == 200 and existing.json():
        return True  # already exists

    # Add new user
    res = requests.post(f"{SUPABASE_URL}/rest/v1/users", json=data, headers=headers)
    return res.status_code == 201

# Fetch all Telegram bot users
def get_all_users():
    res = requests.get(f"{SUPABASE_URL}/rest/v1/users", headers=headers)
    if res.status_code == 200:
        return res.json()
    return []
