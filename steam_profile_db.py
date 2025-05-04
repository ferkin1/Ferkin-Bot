import sqlite3
import os

DB_PATH = os.getenv('DB_PATH', "data/steam_profiles.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS steam_profiles (discord_id TEXT PRIMARY KEY, steam_id TEXT NOT NULL);
        """)
        conn.commit()

def link_steam_profile(discord_id:str, steam_id:str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO steam_profiles (discord_id, steam_id)
            VALUES (?, ?)
            ON CONFLICT(discord_id) DO UPDATE SET steam_id=excluded.steam_id;
            """, (discord_id, steam_id))
        conn.commit()

def get_profile(discord_id:str)-> str | None:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT steam_id FROM steam_profiles WHERE discord_id = ?", (discord_id,))
        result = cursor.fetchone()
        return result[0] if result else None

def unlink_profile(discord_id:str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM steam_profiles WHERE discord_id = ?", (discord_id,))
        conn.commit()

def list_profiles():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM steam_profiles")
        all_profiles = cursor.fetchall()

    return all_profiles
