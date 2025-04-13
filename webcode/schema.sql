DROP TABLE IF EXISTS likes;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS notes;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS note_categories;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE notes (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    user_id INTEGER REFERENCES users,
    created_at TEXT DEFAULT (datetime('now')),
    likes INTEGER DEFAULT 0,
    dislikes INTEGER DEFAULT 0
);

CREATE TABLE note_categories (
    note_id INTEGER REFERENCES notes,
    category_id INTEGER REFERENCES categories,
    PRIMARY KEY (note_id, category_id)
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,
    sent_at TEXT DEFAULT (datetime('now')),
    user_id INTEGER REFERENCES users,
    note_id INTEGER REFERENCES notes,
    parent_id INTEGER REFERENCES messages
);

CREATE TABLE likes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    note_id INTEGER REFERENCES notes,
    is_like BOOLEAN NOT NULL
);

INSERT INTO categories (name) VALUES 
    ('Question'),
    ('Discussion'),
    ('Announcement'),
    ('Other'); 