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
