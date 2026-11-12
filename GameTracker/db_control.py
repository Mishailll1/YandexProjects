import sqlite3

def init_db():
    con = sqlite3.connect("games.db")
    cursor = con.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appid INTEGER UNIQUE NOT NULL,
            name TEXT,
            status TEXT,
            hours INTEGER DEFAULT 0,
            achievements_cur INTEGER DEFAULT 0,
            achievements_all INTEGER DEFAULT 0,
            header TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    con.commit()
    con.close()

def add_game(appid, name, url):
    with sqlite3.connect('games.db') as con:
        cursor = con.cursor()
        cursor.execute("INSERT OR IGNORE INTO games (appid, name, header) VALUES (?, ?, ?)",
                       (appid, name, url))
        con.commit()

def delete_game(appid: int):
    with sqlite3.connect('games.db') as con:
        cursor = con.cursor()
        cursor.execute("DELETE FROM games WHERE appid = ?", (appid,))
        con.commit()

def add_id(steamid: str):
    with sqlite3.connect('games.db') as con:
        cursor = con.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('steamid', ?)",
                       (steamid,))
        con.commit()

def get_id() -> str:
    with sqlite3.connect('games.db') as con:
        cursor = con.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'steamid'")
        data = cursor.fetchone()
        if data:
            return data[0]
        return ''

def get_game_fromdb(appid: int):
    with sqlite3.connect('games.db') as con:
        cursor = con.cursor()
        cursor.execute("SELECT name, status, hours, achievements_cur, achievements_all, header "
                       "FROM games WHERE appid = ?",
                       (appid,))
        return cursor.fetchone()

def update_stats(appid: int, hours: float, curr_ach: int, total_ach: int):
    with sqlite3.connect('games.db') as con:
        cursor = con.cursor()
        cursor.execute("""
        UPDATE games
        SET hours = ?, achievements_cur = ?, achievements_all = ?
        WHERE appid = ?""", (hours, curr_ach, total_ach, appid))
        con.commit()

def get_appids():
    with sqlite3.connect('games.db') as con:
        cursor = con.cursor()
        cursor.execute("SELECT appid FROM games ORDER BY id ASC")
        return [row[0] for row in cursor.fetchall()]

def set_status(appid: int, status: str):
    with sqlite3.connect('games.db') as con:
        cursor = con.cursor()
        cursor.execute("""
        UPDATE games
        SET status = ?
        WHERE appid = ?""", (status, appid))
        con.commit()