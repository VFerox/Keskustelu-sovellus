from flask import session
import db

def get_notes():
    sql = """
        SELECT n.id, n.title, n.user_id,
               m1.content as main_content,
               m1.sent_at as created_at,
               n.likes, n.dislikes,
               GROUP_CONCAT(DISTINCT c.name) as categories,
               l.is_like as user_vote
        FROM notes n
        LEFT JOIN messages m1 ON n.id = m1.note_id
        LEFT JOIN note_categories nc ON n.id = nc.note_id
        LEFT JOIN categories c ON nc.category_id = c.id
        LEFT JOIN likes l ON n.id = l.note_id AND l.user_id = ?
        WHERE m1.id = (SELECT MIN(id) FROM messages WHERE note_id = n.id)
        GROUP BY n.id
        ORDER BY created_at DESC
    """
    user_id = session.get("user_id", None)
    rows = db.query(sql, [user_id])
    
    notes = []
    for row in rows:
        note = {}
        for key in row.keys():
            note[key] = row[key]
        
        reply_sql = """
            SELECT m.content, m.sent_at, u.username
            FROM messages m
            JOIN users u ON m.user_id = u.id
            WHERE m.note_id = ?
            AND m.id != (SELECT MIN(id) FROM messages WHERE note_id = ?)
            ORDER BY m.sent_at ASC
        """
        note["replies"] = db.query(reply_sql, [note["id"], note["id"]])
        notes.append(note)
    
    return notes

def get_note(note_id):
    sql = "SELECT id, title FROM notes WHERE id = ?"
    result = db.query(sql, [note_id])
    if result:
        note = dict(result[0])
        return note
    return None

def get_messages(note_id):
    sql = """SELECT m.id, m.content, m.sent_at, m.user_id, u.username
             FROM messages m, users u
             WHERE m.user_id = u.id AND m.note_id = ?
             ORDER BY m.id"""
    return db.query(sql, [note_id])

def get_message(message_id):
    sql = "SELECT id, content, user_id, note_id FROM messages WHERE id = ?"
    result = db.query(sql, [message_id])
    if result:
        return dict(result[0])
    return None

def add_note(title, content, user_id):
    sql = "INSERT INTO notes (title, user_id, likes, dislikes) VALUES (?, ?, 0, 0)"
    db.execute(sql, [title, user_id])
    note_id = db.last_insert_id()
    add_message(content, user_id, note_id)
    return note_id

def add_message(content, user_id, note_id):
    sql = """INSERT INTO messages (content, sent_at, user_id, note_id) 
             VALUES (?, datetime('now'), ?, ?)"""
    db.execute(sql, [content, user_id, note_id])

def update_message(message_id, content):
    sql = "UPDATE messages SET content = ? WHERE id = ?"
    db.execute(sql, [content, message_id])

def remove_message(message_id):
    sql = "DELETE FROM messages WHERE id = ?"
    db.execute(sql, [message_id])
