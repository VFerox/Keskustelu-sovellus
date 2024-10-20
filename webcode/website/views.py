from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, LikeDislike, Comment, Profile
from . import db
import json
from werkzeug.utils import secure_filename

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  
            db.session.add(new_note) 
            db.session.commit()
            flash('Note added!', category='success')
    all_notes = Note.query.all()
    return render_template("home.html", user=current_user, all_notes=all_notes)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            flash('Note deleted!', category='success')

    return jsonify({})

@views.route('/like-note', methods=['POST'])
@login_required
def like_note():
    note_data = json.loads(request.data)
    note_id = note_data['noteId']
    note = Note.query.get(note_id)

    if note:
        like_dislike = LikeDislike.query.filter_by(user_id=current_user.id, note_id=note_id).first()

        if like_dislike:
            if like_dislike.is_like:
                db.session.delete(like_dislike)
                note.likes -= 1
            else:
                like_dislike.is_like = True
                note.likes += 1
                note.dislikes -= 1
        else:
            new_like = LikeDislike(user_id=current_user.id, note_id=note_id, is_like=True)
            db.session.add(new_like)
            note.likes += 1

        db.session.commit()

    return jsonify({})

@views.route('/dislike-note', methods=['POST'])
@login_required
def dislike_note():
    note_data = json.loads(request.data)
    note_id = note_data['noteId']
    note = Note.query.get(note_id)

    if note:
        like_dislike = LikeDislike.query.filter_by(user_id=current_user.id, note_id=note_id).first()

        if like_dislike:
            if not like_dislike.is_like:
                db.session.delete(like_dislike)
                note.dislikes -= 1
            else:
                like_dislike.is_like = False
                note.likes -= 1
                note.dislikes += 1
        else:
            new_dislike = LikeDislike(user_id=current_user.id, note_id=note_id, is_like=False)
            db.session.add(new_dislike)
            note.dislikes += 1

        db.session.commit()

    return jsonify({})

@views.route('/add-comment', methods=['POST'])
@login_required
def add_comment():
    note_data = json.loads(request.data)
    note_id = note_data['noteId']
    comment_text = note_data['comment']

    note = Note.query.get(note_id)
    if note and comment_text:
        new_comment = Comment(text=comment_text, user_id=current_user.id, note_id=note_id)
        db.session.add(new_comment)
        db.session.commit()

    return jsonify({})


@views.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    bio = request.form.get('bio')
    profile_image = request.form.get('profile_image')

    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)

    profile.bio = bio
    profile.profile_image = profile_image
    db.session.add(profile)
    db.session.commit()

    return jsonify({'success': True})




@views.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@views.route('/delete-comment', methods=['POST'])
@login_required
def delete_comment():
    comment_data = json.loads(request.data)
    comment_id = comment_data['commentId']
    comment = Comment.query.get(comment_id)

    if comment and comment.user_id == current_user.id:
        db.session.delete(comment)
        db.session.commit()

    return jsonify({})


