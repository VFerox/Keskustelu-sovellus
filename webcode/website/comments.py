from . import db

def add_comment(note_id, user_id, comment_text):
    return db.execute(
        'INSERT INTO comment (note_id, user_id, text) VALUES (?, ?, ?)',
        [note_id, user_id, comment_text]
    )

def delete_comment(comment_id, user_id):
    comment = db.query('SELECT user_id FROM comment WHERE id = ?', [comment_id], one=True)
    if comment and comment['user_id'] == user_id:
        db.execute('DELETE FROM comment WHERE id = ?', [comment_id])
        return True
    return False
