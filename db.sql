CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    preference TEXT NOT NULL,
    country TEXT NOT NULL
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    author TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    category TEXT NOT NULL,
    file_path TEXT,
    likes INTEGER DEFAULT 0,
    posted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_anonymous BOOLEAN DEFAULT 0
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    user_name TEXT NOT NULL,
    parent_comment_id INTEGER,
    content TEXT NOT NULL,
    likes INTEGER DEFAULT 0,
    posted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_anonymous BOOLEAN DEFAULT 0
);

