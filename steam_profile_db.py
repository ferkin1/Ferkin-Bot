import supabase as spb
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE")
DB_KEY = os.getenv("DB_API_KEY")
db_table = os.getenv("TABLE_NAME")
client = spb.create_client(DATABASE_URL, DB_KEY)


def link_steam_profile(_discord_id:str, _steam_id:str):
    current_records = client.table(db_table).select("*").eq("discord_id", _discord_id).execute()
    if current_records.data:
        raise ValueError("A Steam Profile is already linked to this Discord account. Please unlink first.")

    client.table(db_table).insert({"discord_id": _discord_id, "steam_id": _steam_id}).execute()

def get_profile(_discord_id:str):
    try:
        result = client.table(db_table).select("steam_id").eq("discord_id",_discord_id).execute()
        data = result.data
        if not data:
            return None
        return data[0]["steam_id"]
    except Exception as e:
        print(f"Error retrieving profile: {e}")
        return None

def unlink_profile(_discord_id:str):
    client.table(db_table).delete().eq("discord_id", _discord_id).execute()