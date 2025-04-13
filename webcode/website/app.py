import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
import config, forum, users, db

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    notes = forum.get_notes()
    return render_template("home.html", notes=notes, user_id=session.get("user_id"))

@app.route("/note/<int:note_id>")
def show_note(note_id):
    note = forum.get_note(note_id)
    messages = forum.get_messages(note_id)
    return render_template("home.html", note=note, messages=messages, user_id=session.get("user_id"))

@app.route("/new_note", methods=["POST"])
def new_note():
    if "user_id" not in session:
        return redirect("/login")
    
    title = request.form["title"]
    content = request.form["content"]
    categories = request.form.getlist("categories")
    user_id = session["user_id"]

    sql = "INSERT INTO notes (title, user_id, likes, dislikes) VALUES (?, ?, 0, 0)"
    db.execute(sql, [title, user_id])
    note_id = db.last_insert_id()

    sql = "INSERT INTO messages (content, user_id, note_id) VALUES (?, ?, ?)"
    db.execute(sql, [content, user_id, note_id])

    if categories:
        sql = "INSERT INTO note_categories (note_id, category_id) VALUES (?, ?)"
        for category_id in categories:
            db.execute(sql, [note_id, category_id])
    
    return redirect("/")

@app.route("/new_message", methods=["POST"])
def new_message():
    if "user_id" not in session:
        return redirect("/login")
    content = request.form["content"]
    user_id = session["user_id"]
    note_id = request.form["note_id"]

    forum.add_message(content, user_id, note_id)
    return redirect("/note/" + str(note_id))

@app.route("/edit/<int:message_id>", methods=["GET", "POST"])
def edit_message(message_id):
    if "user_id" not in session:
        return redirect("/login")
    message = forum.get_message(message_id)

    if request.method == "GET":
        return render_template("home.html", message=message, edit=True, user_id=session.get("user_id"))

    if request.method == "POST":
        content = request.form["content"]
        forum.update_message(message["id"], content)
        return redirect("/note/" + str(message["note_id"]))

@app.route("/remove/<int:message_id>", methods=["GET", "POST"])
def remove_message(message_id):
    if "user_id" not in session:
        return redirect("/login")
    message = forum.get_message(message_id)

    if request.method == "GET":
        return render_template("home.html", message=message, remove=True, user_id=session.get("user_id"))

    if request.method == "POST":
        if "continue" in request.form:
            forum.remove_message(message["id"])
        return redirect("/note/" + str(message["note_id"]))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("sign_up.html", user_id=session.get("user_id"))

    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]

        if password1 != password2:
            return "VIRHE: salasanat eivät ole samat"

        try:
            users.create_user(username, password1)
            user_id = users.check_login(username, password1)
            if user_id:
                session["user_id"] = user_id
                return redirect("/")
            return redirect("/login")
        except sqlite3.IntegrityError:
            return "VIRHE: tunnus on jo varattu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", user_id=session.get("user_id"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["user_id"]
    return redirect("/")

@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]
    
    sql = """
        SELECT 
            COUNT(DISTINCT n.id) as note_count,
            COUNT(DISTINCT m.id) as message_count,
            COUNT(DISTINCT CASE WHEN l.is_like = 1 THEN l.id END) as likes_given,
            COUNT(DISTINCT CASE WHEN l.is_like = 0 THEN l.id END) as dislikes_given
        FROM users u
        LEFT JOIN notes n ON u.id = n.user_id
        LEFT JOIN messages m ON u.id = m.user_id
        LEFT JOIN likes l ON u.id = l.user_id
        WHERE u.id = ?
    """
    profile = db.query(sql, [user_id])[0]

    sql = """
        SELECT n.*, 
               m.content,
               m.sent_at as created_at,
               GROUP_CONCAT(c.name) as categories
        FROM notes n
        LEFT JOIN messages m ON n.id = m.note_id
        LEFT JOIN note_categories nc ON n.id = nc.note_id
        LEFT JOIN categories c ON nc.category_id = c.id
        WHERE n.user_id = ?
        GROUP BY n.id
        ORDER BY m.sent_at DESC
    """
    notes = db.query(sql, [user_id])

    return render_template("profile.html", profile=profile, notes=notes, user_id=user_id)

@app.route("/like", methods=["POST"])
def like():
    if "user_id" not in session:
        return redirect("/login")
    note_id = request.form["note_id"]
    user_id = session["user_id"]
    
    sql = "SELECT is_like FROM likes WHERE user_id = ? AND note_id = ?"
    existing_vote = db.query(sql, [user_id, note_id])
    
    if existing_vote:
        if existing_vote[0]["is_like"]:
            sql = "DELETE FROM likes WHERE user_id = ? AND note_id = ?"
            db.execute(sql, [user_id, note_id])
        else:
            sql = "UPDATE likes SET is_like = ? WHERE user_id = ? AND note_id = ?"
            db.execute(sql, [True, user_id, note_id])
    else:
        sql = "INSERT INTO likes (user_id, note_id, is_like) VALUES (?, ?, ?)"
        db.execute(sql, [user_id, note_id, True])
    
    sql = """
        UPDATE notes 
        SET likes = (SELECT COUNT(*) FROM likes WHERE note_id = ? AND is_like = 1),
            dislikes = (SELECT COUNT(*) FROM likes WHERE note_id = ? AND is_like = 0)
        WHERE id = ?
    """
    db.execute(sql, [note_id, note_id, note_id])
    
    return redirect("/")

@app.route("/dislike", methods=["POST"])
def dislike():
    if "user_id" not in session:
        return redirect("/login")
    note_id = request.form["note_id"]
    user_id = session["user_id"]
    
    sql = "SELECT is_like FROM likes WHERE user_id = ? AND note_id = ?"
    existing_vote = db.query(sql, [user_id, note_id])
    
    if existing_vote:
        if not existing_vote[0]["is_like"]:
            sql = "DELETE FROM likes WHERE user_id = ? AND note_id = ?"
            db.execute(sql, [user_id, note_id])
        else:
            sql = "UPDATE likes SET is_like = ? WHERE user_id = ? AND note_id = ?"
            db.execute(sql, [False, user_id, note_id])
    else:
        sql = "INSERT INTO likes (user_id, note_id, is_like) VALUES (?, ?, ?)"
        db.execute(sql, [user_id, note_id, False])
    
    sql = """
        UPDATE notes 
        SET likes = (SELECT COUNT(*) FROM likes WHERE note_id = ? AND is_like = 1),
            dislikes = (SELECT COUNT(*) FROM likes WHERE note_id = ? AND is_like = 0)
        WHERE id = ?
    """
    db.execute(sql, [note_id, note_id, note_id])
    
    return redirect("/")

@app.route("/profile/<int:user_id>")
def user_profile(user_id):
    sql = """
        SELECT u.username,
               COUNT(DISTINCT n.id) as note_count,
               COUNT(DISTINCT m.id) as message_count,
               COUNT(DISTINCT CASE WHEN l.is_like = 1 THEN l.id END) as likes_given,
               COUNT(DISTINCT CASE WHEN l.is_like = 0 THEN l.id END) as dislikes_given
        FROM users u
        LEFT JOIN notes n ON u.id = n.user_id
        LEFT JOIN messages m ON u.id = m.user_id
        LEFT JOIN likes l ON u.id = l.user_id
        WHERE u.id = ?
        GROUP BY u.id
    """
    profile = db.query(sql, [user_id])[0]

    sql = """
        SELECT n.*, 
               m.content,
               GROUP_CONCAT(c.name) as categories
        FROM notes n
        LEFT JOIN messages m ON n.id = m.note_id
        LEFT JOIN note_categories nc ON n.id = nc.note_id
        LEFT JOIN categories c ON nc.category_id = c.id
        WHERE n.user_id = ?
        GROUP BY n.id
        ORDER BY n.created_at DESC
    """
    notes = db.query(sql, [user_id])

    return render_template("profile.html", profile=profile, notes=notes, user_id=session.get("user_id"))

@app.route("/reply/<int:note_id>", methods=["POST"])
def add_reply(note_id):
    if "user_id" not in session:
        return redirect("/login")
    
    content = request.form["content"]
    user_id = session["user_id"]

    sql = """INSERT INTO messages (content, user_id, note_id) 
             VALUES (?, ?, ?)"""
    db.execute(sql, [content, user_id, note_id])
    
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
