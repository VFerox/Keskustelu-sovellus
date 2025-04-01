from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .database import get_db, query_db

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')
        if note:
            db = get_db()
            db.execute(
                'INSERT INTO note (user_id, data) VALUES (?, ?)',
                (current_user.id, note)
            )
            db.commit()
            flash('Note added successfully!', 'success')
            return redirect(url_for('views.home'))
    
    notes = query_db('''
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
    ''', (current_user.id,))
    
    processed_notes = []
    for note in notes:
        note_dict = dict(note)
        note_dict['user'] = {'username': note['username'], 'id': note['user_id']}
        note_dict['comments'] = []
        note_dict['likes'] = note['likes'] or 0
        note_dict['dislikes'] = note['dislikes'] or 0
        note_dict['user_like_status'] = note['user_like_status']
        
        if note['comments']:
            for comment_str in note['comments'].split(','):
                comment_id, comment_text, comment_user_id, comment_username = comment_str.split('|')
                note_dict['comments'].append({
                    'id': comment_id,
                    'data': comment_text,
                    'user_id': comment_user_id,
                    'user': {'username': comment_username}
                })
        
        processed_notes.append(note_dict)
    
    return render_template('home.html', notes=processed_notes, user=current_user)

@views.route('/add-note', methods=['POST'])
@login_required
def add_note():
    note = request.form.get('note')
    if note:
        db = get_db()
        db.execute(
            'INSERT INTO note (user_id, data) VALUES (?, ?)',
            (current_user.id, note)
        )
        db.commit()
        flash('Note added successfully!', 'success')
    return redirect(url_for('views.home'))

@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    note_id = request.form.get('note_id')
    if note_id:
        db = get_db()
        note = query_db('SELECT user_id FROM note WHERE id = ?', (note_id,), one=True)
        if note and note['user_id'] == current_user.id:
            db.execute('DELETE FROM note WHERE id = ?', (note_id,))
            db.commit()
            flash('Note deleted successfully!', 'success')
    return redirect(url_for('views.home'))

@views.route('/like-note', methods=['POST'])
@login_required
def like_note():
    note_id = request.form.get('note_id')
    if note_id:
        db = get_db()
        existing = db.execute(
            'SELECT is_like FROM like_dislike WHERE user_id = ? AND note_id = ?',
            (current_user.id, note_id)
        ).fetchone()
        
        if existing:
            if existing['is_like'] == 1:
                db.execute(
                    'DELETE FROM like_dislike WHERE user_id = ? AND note_id = ?',
                    (current_user.id, note_id)
                )
                db.execute(
                    'UPDATE note SET likes = likes - 1 WHERE id = ?',
                    (note_id,)
                )
            else:
                db.execute(
                    'UPDATE like_dislike SET is_like = 1 WHERE user_id = ? AND note_id = ?',
                    (current_user.id, note_id)
                )
                db.execute(
                    'UPDATE note SET dislikes = dislikes - 1, likes = likes + 1 WHERE id = ?',
                    (note_id,)
                )
        else:
            db.execute(
                'INSERT INTO like_dislike (user_id, note_id, is_like) VALUES (?, ?, ?)',
                (current_user.id, note_id, 1)
            )
            db.execute(
                'UPDATE note SET likes = likes + 1 WHERE id = ?',
                (note_id,)
            )
        
        db.commit()
    return redirect(url_for('views.home'))

@views.route('/dislike-note', methods=['POST'])
@login_required
def dislike_note():
    note_id = request.form.get('note_id')
    if note_id:
        db = get_db()
        existing = db.execute(
            'SELECT is_like FROM like_dislike WHERE user_id = ? AND note_id = ?',
            (current_user.id, note_id)
        ).fetchone()
        
        if existing:
            if existing['is_like'] == 0:
                db.execute(
                    'DELETE FROM like_dislike WHERE user_id = ? AND note_id = ?',
                    (current_user.id, note_id)
                )
                db.execute(
                    'UPDATE note SET dislikes = dislikes - 1 WHERE id = ?',
                    (note_id,)
                )
            else:
                db.execute(
                    'UPDATE like_dislike SET is_like = 0 WHERE user_id = ? AND note_id = ?',
                    (current_user.id, note_id)
                )
                db.execute(
                    'UPDATE note SET likes = likes - 1, dislikes = dislikes + 1 WHERE id = ?',
                    (note_id,)
                )
        else:
            db.execute(
                'INSERT INTO like_dislike (user_id, note_id, is_like) VALUES (?, ?, ?)',
                (current_user.id, note_id, 0)
            )
            db.execute(
                'UPDATE note SET dislikes = dislikes + 1 WHERE id = ?',
                (note_id,)
            )
        
        db.commit()
    return redirect(url_for('views.home'))

@views.route('/add-comment', methods=['POST'])
@login_required
def add_comment():
    note_id = request.form.get('note_id')
    comment = request.form.get('comment')
    if note_id and comment:
        db = get_db()
        db.execute(
            'INSERT INTO comment (note_id, user_id, text) VALUES (?, ?, ?)',
            (note_id, current_user.id, comment)
        )
        db.commit()
        flash('Comment added successfully!', 'success')
    return redirect(url_for('views.home'))

@views.route('/delete-comment', methods=['POST'])
@login_required
def delete_comment():
    comment_id = request.form.get('comment_id')
    if comment_id:
        db = get_db()
        comment = query_db('SELECT user_id FROM comment WHERE id = ?', (comment_id,), one=True)
        if comment and comment['user_id'] == current_user.id:
            db.execute('DELETE FROM comment WHERE id = ?', (comment_id,))
            db.commit()
            flash('Comment deleted successfully!', 'success')
    return redirect(url_for('views.home'))

@views.route('/profile')
@login_required
def profile():
    user_notes = query_db('''
        SELECT n.*, 
               (SELECT COUNT(*) FROM like_dislike WHERE note_id = n.id AND is_like = 1) as likes,
               (SELECT COUNT(*) FROM like_dislike WHERE note_id = n.id AND is_like = 0) as dislikes
        FROM note n
        WHERE n.user_id = ?
        ORDER BY n.date DESC
    ''', (current_user.id,))
    
    return render_template('profile.html', user=current_user, notes=user_notes)

@views.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    bio = request.form.get('bio')
    profile_image = request.form.get('profile_image')
    
    db = get_db()
    existing_profile = query_db('SELECT id FROM profile WHERE user_id = ?', (current_user.id,), one=True)
    
    if existing_profile:
        db.execute(
            'UPDATE profile SET bio = ?, profile_image = ? WHERE user_id = ?',
            (bio, profile_image, current_user.id)
        )
    else:
        db.execute(
            'INSERT INTO profile (user_id, bio, profile_image) VALUES (?, ?, ?)',
            (current_user.id, bio, profile_image)
        )
    
    db.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('views.profile'))


