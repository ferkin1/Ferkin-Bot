import sqlite3
import os

DB_FILE = 'steam_prof.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS steam_profiles (discord_id TEXT PRIMARY KEY, steam_id TEXT NOT NULL);
    """)
    conn.commit()
    conn.close()

def link_steam_profile(discord_id:str, steam_id:str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO steam_profiles (discord_id, steam_id)
        VALUES (?, ?)
        ON CONFLICT(discord_id) DO UPDATE SET steam_id=excluded.steam_id;
        """, (discord_id, steam_id))
    conn.commit()
    conn.close()

def get_profile(discord_id:str)-> str | None:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT steam_id FROM steam_profiles WHERE discord_id = ?", (discord_id,))
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None

def unlink_profile(discord_id:str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM steam_profiles WHERE discord_id = ?", (discord_id,))
    conn.commit()
    conn.close()

def list_profiles():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM steam_profiles")
    all_profiles = cursor.fetchall()
    conn.close()

    return all_profiles
