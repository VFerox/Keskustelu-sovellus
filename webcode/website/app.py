import sqlite3
from flask import Flask, redirect, render_template, request, session, abort
import config, forum, users, db, os, secrets
from functools import wraps
from flask import url_for

app = Flask(__name__)
app.secret_key = config.secret_key

@app.template_filter('nl2br')
def nl2br(s):
    if s is None:
        return ''
    return s.replace('\n', '<br>\n')

@app.before_request
def _ensure_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)

@app.before_request
def _csrf_protect():
    if request.method == 'POST':
        token = request.form.get('csrf_token')
        if not token or token != session['csrf_token']:
            abort(400)

@app.context_processor
def inject_csrf():
    return {'csrf_token': session.get('csrf_token')}

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@login_required
def index():
    page       = int(request.args.get("page", 1))      
    per_page   = 10
    notes      = forum.get_notes_paginated(page, per_page)
    total      = forum.count_notes()
    total_pages = (total + per_page - 1) // per_page
    return render_template(
        "home.html",
        notes=notes,
        page=page,
        total_pages=total_pages,
        user_id=session["user_id"],
        url_for=url_for                              
    )

@app.route('/note/<int:note_id>')
@login_required
def show_note(note_id):
    note = forum.get_note(note_id)
    messages = forum.get_messages(note_id)
    return render_template('note.html', note=note, messages=messages, user_id=session['user_id'])

@app.route('/new_note', methods=['POST'])
@login_required
def new_note():
    title = request.form.get('title','').strip()
    content = request.form.get('content','').strip()
    if not title or not content:
        abort(400)
    note_id = db.execute(
        "INSERT INTO notes (title, user_id, likes, dislikes) VALUES (?, ?, 0, 0)",
        [title, session['user_id']]
    )
    db.execute(
        "INSERT INTO messages (content, user_id, note_id) VALUES (?, ?, ?)",
        [content, session['user_id'], note_id]
    )
    return redirect("/")

@app.route('/new_message', methods=['POST'])
@login_required
def new_message():
    content = request.form.get('content','').strip()
    try:
        note_id = int(request.form.get('note_id',''))
    except:
        abort(400)
    if not content or forum.get_note(note_id) is None:
        abort(400)
    forum.add_message(content, session['user_id'], note_id)
    return redirect(f'/note/{note_id}')

@app.route('/edit/<int:message_id>', methods=['GET','POST'])
@login_required
def edit_message(message_id):
    message = forum.get_message(message_id)
    if message['user_id']!=session['user_id']:
        abort(403)
    if request.method=='GET':
        return render_template('note.html', note=forum.get_note(message['note_id']), messages=forum.get_messages(message['note_id']), edit=message)
    content = request.form.get('content','').strip()
    if not content:
        abort(400)
    forum.update_message(message_id, content)
    return redirect(f"/note/{message['note_id']}")

@app.route('/remove/<int:message_id>', methods=['GET','POST'])
@login_required
def remove_message(message_id):
    message = forum.get_message(message_id)
    if message['user_id']!=session['user_id']:
        abort(403)
    if request.method=='GET':
        return render_template('note.html', note=forum.get_note(message['note_id']), messages=forum.get_messages(message['note_id']), remove=message)
    forum.remove_message(message_id)
    return redirect(f"/note/{message['note_id']}")

@app.route("/like", methods=["POST"])
@login_required
def like():
    note_id = int(request.form["note_id"])
    forum.add_like(note_id, session["user_id"], True)
    return redirect(request.referrer or "/")

@app.route("/dislike", methods=["POST"])
@login_required
def dislike():
    note_id = int(request.form["note_id"])
    forum.add_like(note_id, session["user_id"], False)
    return redirect(request.referrer or "/")

@app.route("/reply/<int:note_id>", methods=["POST"])
@login_required
def reply(note_id):
    content = request.form.get("content", "").strip()
    if not content or forum.get_note(note_id) is None:
        abort(400)
    forum.add_message(content, session["user_id"], note_id)
    return redirect("/")

@app.route('/search')
@login_required
def search():
    q       = request.args.get("q", "").strip()
    if not q:
        return redirect("/")
    like_q  = f"%{q}%"
    base_sql = """
        SELECT n.id, n.title, u.username,
               m.content, m.sent_at
          FROM notes n
     LEFT JOIN (
         SELECT note_id, content, sent_at
           FROM messages
          WHERE id IN (
              SELECT MIN(id) FROM messages GROUP BY note_id
          )
     ) m ON m.note_id = n.id
     JOIN users u ON u.id = n.user_id
         WHERE n.title LIKE ? OR m.content LIKE ?
         ORDER BY m.sent_at DESC
    """
    page       = int(request.args.get("page", 1))
    per_page   = 10
    offset     = (page - 1) * per_page
    results    = db.query(base_sql + " LIMIT ? OFFSET ?", [like_q, like_q, per_page, offset])
    total      = db.query(
        "SELECT COUNT(DISTINCT n.id) AS c FROM notes n JOIN messages m ON n.id=m.note_id WHERE n.title LIKE ? OR m.content LIKE ?",
        [like_q, like_q],
        one=True
    )["c"]
    total_pages = (total + per_page - 1) // per_page
    return render_template(
        "search.html",
        results=results,
        q=q,
        page=page,
        total_pages=total_pages,
        user_id=session["user_id"],
        url_for=url_for
    )

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='GET':
        return render_template('sign_up.html')
    u=request.form['username']
    p1=request.form['password1']
    p2=request.form['password2']
    bio       = request.form.get("bio","").strip()
    if p1!=p2:
        return 'ERROR'
    try:
        users.create_user(u, p1, bio)
        session['user_id']=users.check_login(u,p1)
        return redirect('/')
    except sqlite3.IntegrityError:
        return 'ERROR'
    
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    u=request.form['username']
    p=request.form['password']
    uid=users.check_login(u,p)
    if uid:
        session['user_id']=uid
        return redirect('/')
    return 'ERROR'

@app.route('/logout')
def logout():
    session.pop('user_id',None)
    return redirect('/login')


@app.route("/profile")
@login_required
def profile():
    return redirect(f"/profile/{session['user_id']}")

@app.route("/profile/<int:user_id>")
@login_required
def user_profile(user_id):
    profile = db.query(
        "SELECT id, username, bio FROM users WHERE id = ?",
        [user_id],
        one=True
    )
    sql = """
        SELECT
            n.id,
            n.title,
            m.content,
            m.sent_at   AS created_at,
            GROUP_CONCAT(c.name) AS categories
        FROM notes n
        LEFT JOIN (
            SELECT note_id, content, sent_at
            FROM messages
            WHERE id IN (
                SELECT MIN(id) FROM messages GROUP BY note_id
            )
        ) m ON m.note_id = n.id
        LEFT JOIN note_categories nc ON nc.note_id = n.id
        LEFT JOIN categories c ON c.id = nc.category_id
        WHERE n.user_id = ?
        GROUP BY n.id
        ORDER BY m.sent_at DESC
    """
    notes = db.query(sql, [user_id])
    return render_template(
        "profile.html",
        profile=profile,
        notes=notes,
        user_id=session["user_id"]
    )


if __name__=='__main__':
    app.run(debug=True)
