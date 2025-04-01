from flask_login import UserMixin
from .database import query_db, get_db


class User(UserMixin):
    def __init__(self, id, email, username):
        self.id = id
        self.email = email
        self.username = username

    @staticmethod
    def get(user_id):
        user = query_db('SELECT * FROM user WHERE id = ?', (user_id,), one=True)
        if user is None:
            return None
        return User(user['id'], user['email'], user['username'])

    @staticmethod
    def get_by_email(email):
        user = query_db('SELECT * FROM user WHERE email = ?', (email,), one=True)
        if user is None:
            return None
        return User(user['id'], user['email'], user['username'])

    @staticmethod
    def create(email, password, username):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO user (email, password, username) VALUES (?, ?, ?)',
            (email, password, username)
        )
        db.commit()
        return User.get(cursor.lastrowid)

    @property
    def profile(self):
        profile = query_db('SELECT * FROM profile WHERE user_id = ?', (self.id,), one=True)
        return profile if profile else None

    @property
    def notes(self):
        return query_db('SELECT * FROM note WHERE user_id = ? ORDER BY date DESC', (self.id,))