import os, sqlite3
def get_db_connection():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    db_path = os.path.join(parent_dir, "database.db")
    connection = sqlite3.connect(db_path, timeout=30, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    
    connection.execute("CREATE INDEX IF NOT EXISTS idx_messages_note_id ON messages(note_id)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_likes_note_id    ON likes(note_id)")
    return connection

def execute(sql, params=None):
    conn = get_db_connection()
    cur = conn.cursor()
    if params:
        cur.execute(sql, params)
    else:
        cur.execute(sql)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id

def query(sql, params=None, one=False):
    conn = get_db_connection()
    cur = conn.cursor()
    if params:
        cur.execute(sql, params)
    else:
        cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    if one:
        return rows[0] if rows else None
    return rows


def last_insert_id():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT last_insert_rowid()")
        return cursor.fetchone()[0]
    finally:
        connection.close()
