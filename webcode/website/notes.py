from . import db

def get_notes(user_id):
    return db.query('''
        SELECT n.*, u.username, u.id as user_id,
               GROUP_CONCAT(c.id || '|' || c.text || '|' || c.user_id || '|' || cu.username) as comments,
               (SELECT COUNT(*) FROM like_dislike WHERE note_id = n.id AND is_like = 1) as likes,
               (SELECT COUNT(*) FROM like_dislike WHERE note_id = n.id AND is_like = 0) as dislikes,
               (SELECT is_like FROM like_dislike WHERE note_id = n.id AND user_id = ?) as user_like_status
        FROM note n
        JOIN user u ON n.user_id = u.id
        LEFT JOIN comment c ON n.id = c.note_id
        LEFT JOIN user cu ON c.user_id = cu.id
        GROUP BY n.id
        ORDER BY n.date DESC
    ''', [user_id])

def add_note(user_id, note_text):
    return db.execute(
        'INSERT INTO note (user_id, data) VALUES (?, ?)',
        [user_id, note_text]
    )

def delete_note(note_id, user_id):
    note = db.query('SELECT user_id FROM note WHERE id = ?', [note_id], one=True)
    if note and note['user_id'] == user_id:
        db.execute('DELETE FROM note WHERE id = ?', [note_id])
        return True
    return False

def handle_like(note_id, user_id, is_like):
    existing = db.query(
        'SELECT is_like FROM like_dislike WHERE user_id = ? AND note_id = ?',
        [user_id, note_id], one=True
    )
    
    if existing:
        if existing['is_like'] == is_like:
            db.execute(
                'DELETE FROM like_dislike WHERE user_id = ? AND note_id = ?',
                [user_id, note_id]
            )
            db.execute(
                f'UPDATE note SET {"likes" if is_like else "dislikes"} = {"likes" if is_like else "dislikes"} - 1 WHERE id = ?',
                [note_id]
            )
        else:
            db.execute(
                'UPDATE like_dislike SET is_like = ? WHERE user_id = ? AND note_id = ?',
                [is_like, user_id, note_id]
            )
            db.execute(
                f'UPDATE note SET likes = likes {"+" if is_like else "-"} 1, dislikes = dislikes {"+" if not is_like else "-"} 1 WHERE id = ?',
                [note_id]
            )
    else:
        db.execute(
            'INSERT INTO like_dislike (user_id, note_id, is_like) VALUES (?, ?, ?)',
            [user_id, note_id, is_like]
        )
        db.execute(
            f'UPDATE note SET {"likes" if is_like else "dislikes"} = {"likes" if is_like else "dislikes"} + 1 WHERE id = ?',
            [note_id]
        )
