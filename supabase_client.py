from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def add_user(telegram_id, username):
    existing = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
    if not existing.data:
        supabase.table("users").insert({
            "telegram_id": telegram_id,
            "username": username or ""
        }).execute()

def get_all_users():
    return supabase.table("users").select("telegram_id").execute().data
