from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import notes, comments

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')
        if note:
            notes.add_note(current_user.id, note)
            flash('Note added successfully!', 'success')
            return redirect(url_for('views.home'))
    
    notes_data = notes.get_notes(current_user.id)
    
    processed_notes = []
    for note in notes_data:
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
        notes.add_note(current_user.id, note)
        flash('Note added successfully!', 'success')
    return redirect(url_for('views.home'))

@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    note_id = request.form.get('note_id')
    if note_id and notes.delete_note(note_id, current_user.id):
        flash('Note deleted successfully!', 'success')
    return redirect(url_for('views.home'))

@views.route('/like-note', methods=['POST'])
@login_required
def like_note():
    note_id = request.form.get('note_id')
    if note_id:
        notes.handle_like(note_id, current_user.id, True)
    return redirect(url_for('views.home'))

@views.route('/dislike-note', methods=['POST'])
@login_required
def dislike_note():
    note_id = request.form.get('note_id')
    if note_id:
        notes.handle_like(note_id, current_user.id, False)
    return redirect(url_for('views.home'))

@views.route('/add-comment', methods=['POST'])
@login_required
def add_comment():
    note_id = request.form.get('note_id')
    comment = request.form.get('comment')
    if note_id and comment:
        comments.add_comment(note_id, current_user.id, comment)
        flash('Comment added successfully!', 'success')
    return redirect(url_for('views.home'))

@views.route('/delete-comment', methods=['POST'])
@login_required
def delete_comment():
    comment_id = request.form.get('comment_id')
    if comment_id and comments.delete_comment(comment_id, current_user.id):
        flash('Comment deleted successfully!', 'success')
    return redirect(url_for('views.home'))

@views.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


