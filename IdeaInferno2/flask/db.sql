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

CREATE TABLE likes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (post_id) REFERENCES posts(id),
    UNIQUE (user_id, post_id)
);

CREATE TABLE follows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    follower_id INTEGER NOT NULL,
    follower_name TEXT NOT NULL,
    followed_id INTEGER NOT NULL,
    followed_name TEXT NOT NULL,
    FOREIGN KEY (follower_id) REFERENCES users(id),
    FOREIGN KEY (followed_id) REFERENCES users(id),
    UNIQUE (follower_id, followed_id)
);

CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER,
    receiver_id INTEGER,
    content TEXT,
    file_type TEXT, -- e.g., 'image', 'video', 'pdf'
    file_url TEXT, -- path or URL to the uploaded file
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT 0,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id)
);


SELECT users.id, users.username,
COUNT(CASE WHEN messages.is_read = 0 AND messages.receiver_id = ? THEN 1 END) AS unread_count,
messages.content AS last_message, messages.timestamp AS last_message_time 
FROM users JOIN messages ON (users.id = messages.sender_id OR users.id = messages.receiver_id) 
WHERE (messages.sender_id = ? OR messages.receiver_id = ?) 
AND users.id != ? GROUP BY users.id, users.username 
HAVING messages.timestamp = (SELECT MAX(timestamp) FROM messages 
WHERE (sender_id = users.id AND receiver_id = ?) OR (sender_id = ? AND receiver_id = users.id)) 
ORDER BY last_message_time DESC", session['id'], session['id'], session['id'], session['id'], session['id'], session['id']

db.execute("SELECT users.id, users.username, COUNT(CASE WHEN messages.is_read = 0 AND messages.receiver_id = ? THEN 1 END) AS unread_count, messages.content AS last_message, messages.timestamp AS last_message_time FROM users JOIN messages ON (users.id = messages.sender_id OR users.id = messages.receiver_id) WHERE (messages.sender_id = ? OR messages.receiver_id = ?) AND users.id != ? GROUP BY users.id, users.username HAVING messages.timestamp = (SELECT MAX(timestamp) FROM messages WHERE (sender_id = users.id AND receiver_id = ?) OR (sender_id = ? AND receiver_id = users.id)) ORDER BY last_message_time DESC ", session['id'], session['id'], session['id'], session['id'], session['id'], session['id'])