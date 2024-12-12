import os
import uuid
from cs50 import SQL
from flask import Flask, flash, redirect, url_for, render_template, request, session, jsonify
from flask_socketio import SocketIO, emit, join_room
from flask import session, request, Flask, flash, redirect, url_for, session, logging, render_template, send_from_directory
from flask_session import Session
from flask_mail import Mail, Message
from random import randint
from werkzeug.security import check_password_hash, generate_password_hash
from forms import RegisterForm, ArticleForm, EditForm, extract_usernames
from datetime import datetime
from helpers import login_required, valid_email, is_logged_in

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'pdf', 'gif', 'mp4'}
mail = Mail(app)
# app.config['MAIL_SERVER']

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower in app.config['ALLOWED_EXTENSIONS']

#confiq  Database
db = SQL("sqlite:///idea.db")

def get_like_count(id):
    return db.execute("SELECT COUNT(*) FROM likes WHERE post_id = ?", id)[0]['COUNT(*)']

def add_notification(user_id, message):
    timestamp = datetime.now()
    db.execute("INSERT INTO notifications (user_id, message, timestamp, is_read) VALUES (?, ?, ?, ?)", user_id, message, timestamp, 0)

#static file path
@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

@app.route("/")
def index():
    form = RegisterForm(request.form)
    return render_template("index.html", form=form)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/vision")
def vision():
    return render_template("vision.html")

#register
@app.route('/register', methods=['POST'])
def register():
    form = RegisterForm(request.form)
    name = form.name.data
    email = form.email.data
    username = form.username.data
    prefernce = form.type.data
    country = form.country.data
    password = generate_password_hash(str(form.password.data), method='pbkdf2', salt_length=16)
    db_username_check = db.execute("SELECT * FROM users WHERE username = ?", username)
    db_email_check = db.execute("SELECT * FROM users WHERE email = ?", email)

    if len(db_username_check) == 1:
        flash('Username Already Taken', 'danger')
        # return redirect(url_for('register'))
    elif db_email_check:
        flash('Email Already Taken', 'danger')
        # return redirect(url_for('register'))
    elif not prefernce:
        flash('Must Select a preference', 'danger')
        # return redirect(url_for('register'))
    
    # Set db
    db.execute("INSERT INTO users (name, email, username, password, preference, country) VALUES(?, ?, ?, ?, ?, ?)", name, email, username, password, prefernce, country)
    result = db.execute("SELECT * FROM users WHERE username = ?", username)
    message = f"Welcome To IdeaInferno, From Admin"
    add_notification(result[0]['id'], message)
    #flash
    flash('You are Now Registered and can log in', 'success')

    #redirect to home
    return redirect(url_for('index'))

# login
@app.route('/login', methods=['POST'])
def login():
    # get form fields
    username = request.form.get('username')
    password_candidate = request.form.get('password')

    result = db.execute("SELECT * FROM users WHERE username = ?", username)
    if username == 'ADMIN' and password_candidate == 'admin':
        session['admin'] = username
        flash('Logged in as Admin', 'success')
        return redirect(url_for('admindashboard'))
    
    if len(result) != 1:
        # ensure username exist
        flash('Username Does Not Exist', 'danger')
        return redirect(url_for('index'))
    #compare passwords
    if not check_password_hash(result[0]['password'], password_candidate): 
        flash('Invalid Password', 'danger')
        return redirect(url_for('index'))
    else:
        session['logged_in'] = True
        session['username'] = username
        session['id'] = result[0]['id']
        session['email'] = result[0]['email']

        flash('You are now logged in', 'success')
        return redirect(url_for('home'))

#logout
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
    flash("Successfully Logged Out", 'success')
    # Redirect user to login form
    return redirect("/")

@app.route("/home")
@is_logged_in
def home():
    username = session['username']
    profile = username[0].capitalize()
    posts = db.execute("SELECT * FROM posts ORDER BY posted_at DESC")
    notifications = db.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY timestamp DESC", (session['id'],))
    unread_count = db.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0", (session['id'],))[0]['COUNT(*)']
    unread_message = db.execute("SELECT COUNT(*) FROM messages WHERE receiver_id = ? AND is_read = 0", (session['id'],))[0]['COUNT(*)']
    form = ArticleForm(request.form)

    return render_template('home.html', unread_count=unread_count, unread_message=unread_message, notifications=notifications, get_profile=get_profile, posts=posts, profile=profile, get_liked=get_liked, form=form, get_like_count=get_like_count)

def get_liked(id):
    liked = db.execute("SELECT * FROM likes WHERE user_id = ? AND post_id = ?", session['id'], id)
    if liked:
        return True
    return False

def get_profile(name):
    return name[0].capitalize()

#add post
@app.route('/add_post', methods=['POST'])
@is_logged_in
def add_post():
    form = ArticleForm(request.form)
    title = form.title.data
    body = form.body.data
    category = form.category.data
    anonymous = form.anonymous.data
    image = request.files['image']
    if not category:
        flash('Must select a category', 'danger')
        return redirect(url_for('home'))
    if image:
        filename = str(uuid.uuid1())+os.path.splitext(image.filename)[1]
        image.save(os.path.join("static/uploads", filename))
    else:
        filename = None
    
    if anonymous == 'yes':
        isanonymous = 1
        db.execute("INSERT INTO posts (title, body, file_path, user_id, author, category, is_anonymous) VALUES(?, ?, ?, ?, ?, ?, ?)", title, body, filename, session['id'], 'Anonymous', category, isanonymous)
    else:
        isanonymous = 0

    db.execute("INSERT INTO posts (title, body, file_path, user_id, author, category, is_anonymous) VALUES(?, ?, ?, ?, ?, ?, ?)", title, body, filename, session['id'], session['username'], category, isanonymous)
    flash('Posted', 'success')

    return redirect(request.referrer or url_for('home'))

#single article
@app.route("/post/<string:id>")
def post(id):
    count = db.execute('SELECT COUNT(*) FROM posts')[0]['COUNT(*)']

    if(int(id) > int(count)):
        flash('Post Not Available', 'danger')
        return redirect(url_for('home'))
    user_liked = False
    if 'id' in session:
        user_id = session['id']
        liked = db.execute("SELECT * FROM likes WHERE user_id = ? AND post_id = ?", user_id, id)
        if liked:
            user_liked = True
    like_count = db.execute("SELECT COUNT(*) FROM likes WHERE post_id = ?", (id,))[0]['COUNT(*)']


    post = db.execute("SELECT * FROM posts WHERE id = ?", id)[0]
    comments = db.execute("SELECT * FROM comments WHERE post_id = ? ORDER BY posted_at DESC", id)
    no_of_comments = db.execute('SELECT COUNT(*) FROM comments WHERE post_id = ?', id)[0]['COUNT(*)']
    return render_template('post.html', post=post, like_count=like_count, comments=comments, no_of_comments=no_of_comments, user_liked=user_liked)

#add comment
@app.route('/add_comment', methods=['POST'])
@is_logged_in
def add_comment():
    text = request.form.get('text')
    post_id = request.form.get('post_id')
    username = session['username']
    if not text:
        flash('Please Enter a text', 'danger')
        return redirect(url_for('post', id=post_id))
    db.execute('INSERT INTO comments (post_id, user_name, user_id, content) VALUES (?, ?, ?, ?)', post_id, username, session['id'], text)
    
    return redirect(request.referrer or url_for('post'))

@app.route('/toggle_like/<int:post_id>', methods=['POST'])
def toggle_like(post_id):
    if 'id' not in session:
        flash('You must be logged in to like posts.', 'danger')
        return redirect(url_for('index')) # Redirect to the homepage or login page

    user_id = session['id']

    # Check if the user has already liked the post
    like = db.execute("SELECT * FROM likes WHERE user_id = ? AND post_id = ?", user_id, post_id)

    if like:
        # If the user has liked the post, remove the like (unlike)
        db.execute("DELETE FROM likes WHERE user_id = ? AND post_id = ?", user_id, post_id)
    else:
        # If the user has not liked the post, add a like
        db.execute("INSERT INTO likes (user_id, post_id) VALUES (?, ?)", user_id, post_id)

    return redirect(request.referrer or url_for('post'))

@app.route('/profile')
@is_logged_in
def profile():
    username = session['username']
    posts = db.execute("SELECT * FROM posts WHERE user_id = ? ORDER BY posted_at DESC", session['id'])
    post_count = db.execute("SELECT COUNT(*) FROM posts WHERE user_id = ?", session['id'])[0]['COUNT(*)']
    # Count the number of followers for this user
    followers_count = db.execute("SELECT COUNT(*) FROM follows WHERE followed_id = ?", (session['id'],))[0]['COUNT(*)']
    # Count the number of people this user is following
    following_count = db.execute("SELECT COUNT(*) FROM follows WHERE follower_id = ?", (session['id']))[0]['COUNT(*)']
    user = db.execute("SELECT * FROM users WHERE username = ?", username)
    profile = username[0].capitalize()
    return render_template('profile.html', user=user, posts=posts, profile=profile, post_count=post_count, following_count=following_count, followers_count=followers_count)

@app.route('/user/<string:username>')
@is_logged_in
def user(username):
    if username == session['username']:
        return redirect(url_for('profile'))

    user = db.execute("SELECT * FROM users WHERE username = ?", username)
    post_count = db.execute("SELECT COUNT(*) FROM posts WHERE user_id = ?", user[0]['id'])[0]['COUNT(*)']
    posts = db.execute("SELECT * FROM posts WHERE user_id = ? ORDER BY posted_at DESC", user[0]['id'])

    user_id = user[0]['id']
    # Count the number of followers for this user
    followers_count = db.execute("SELECT COUNT(*) FROM follows WHERE followed_id = ?", (user_id,))[0]['COUNT(*)']
    
    # Count the number of people this user is following
    following_count = db.execute("SELECT COUNT(*) FROM follows WHERE follower_id = ?", (user_id,))[0]['COUNT(*)']

    # Check if the current logged-in user is following this user
    is_following = False
    follows_you = False
    if 'id' in session:
        current_user_id = session['id']
        following = db.execute("SELECT * FROM follows WHERE follower_id = ? AND followed_id = ?", current_user_id, user_id)
        follows = db.execute("SELECT * FROM follows WHERE follower_id = ? AND followed_id = ?",user_id, current_user_id)
        if following:
            is_following = True
        if follows:
            follows_you = True
    profile = user[0]['username'][0].capitalize()
    return render_template('user.html', posts=posts, follows_you=follows_you, post_count=post_count, user=user, profile=profile, followers_count=followers_count, following_count=following_count, is_following=is_following)
    
@app.route('/toggle_follow/<string:id>', methods=['POST'])
@is_logged_in
def toggle_follow(id):
    if 'id' not in session:
        flash('You must be logged in to follow users.', 'error')
        return redirect(url_for('index')) # Redirect to the homepage or login page

    follower_id = session['id']
    follower_name = session['username']
    followed_name = db.execute('SELECT username FROM users WHERE id = ?', id)[0]['username']

    # Check if the current user is already following the other user
    follow = db.execute("SELECT * FROM follows WHERE follower_id = ? AND followed_id = ?", follower_id, id)

    if follow:
        # If following, remove the follow relationship (unfollow)
        db.execute("DELETE FROM follows WHERE follower_id = ? AND followed_id = ?", follower_id, id)
        unfollowed_user = db.execute('SELECT username FROM users WHERE id = ?', session['id'])[0]['username']
        if unfollowed_user:
            message = f"{unfollowed_user} Unfollowed you"
            add_notification(id, message)
        unfollowed_user2 = db.execute('SELECT username FROM users WHERE id = ?', id)[0]['username'] 
        if unfollowed_user2:   
            message2 = f"You Unfollowed {unfollowed_user2} "
            add_notification(session['id'], message2)
    else:
        # If not following, add a follow relationship
        db.execute("INSERT INTO follows (follower_id, follower_name, followed_id, followed_name) VALUES (?, ?, ?, ?)", follower_id, follower_name, id, followed_name)
        followed_user = db.execute('SELECT username FROM users WHERE id = ?', session['id'])[0]['username']
        if followed_user:
            message = f"{followed_user} started following you"
            add_notification(id, message)
        followed_user2 = db.execute('SELECT username FROM users WHERE id = ?', id)[0]['username']
        if followed_user2:
            message2 = f"You followed {followed_user2} "
            add_notification(session['id'], message2)
    return redirect(request.referrer or url_for('user'))

@app.route('/mark-notifications-read', methods=['POST'])
def mark_notifications_read():
    user_id = session['id']
    if user_id:
        db.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
        return jsonify(success=True)
    return jsonify(success=False), 400

@app.route('/mark-message-read/<int:user_id>/read', methods=['POST'])
def mark_message_read(user_id):
    if user_id:
        db.execute("UPDATE messages SET is_read = 1 WHERE sender_id = ? AND receiver_id = ?", user_id, session['id'])
        return jsonify(success=True)
    return jsonify(success=False), 400

def get_unread_message(sender_id):
    pass

@app.route('/inbox')
@is_logged_in
def inbox():
    user_id = session['id']  # Replace with the logged-in user's ID
    # Fetch users the current user follows
    follows = db.execute('SELECT * FROM follows WHERE follower_id = ?', (user_id,))
    senders = db.execute("SELECT users.id, users.username, m.content AS last_message, m.timestamp AS last_message_time, SUM(CASE WHEN m.is_read = 0 AND m.receiver_id = ? THEN 1 END) AS unread_count FROM users JOIN messages m ON (users.id = m.sender_id OR users.id = m.receiver_id) WHERE (m.sender_id = ? OR m.receiver_id = ?) AND users.id != ? AND m.timestamp = (SELECT MAX(timestamp) FROM messages WHERE (sender_id = m.sender_id AND receiver_id = m.receiver_id) OR (sender_id = m.receiver_id AND receiver_id = m.sender_id)) GROUP BY users.id ORDER BY last_message_time DESC", session['id'], session['id'], session['id'], session['id'])

    for convo in senders:
        if len(convo['last_message']) > 25:
            convo['last_message'] = convo['last_message'][:25] + '...'
            
    return render_template('inbox.html', follows=follows, get_unread=get_unread, senders=senders, current=None, messages=None)

def get_unread(user_id):
    return db.execute('SELECT COUNT(*) FROM messages WHERE sender_id = ? AND receiver_id = ? AND is_read = 0', user_id, session['id'])[0]['COUNT(*)']

@app.route('/inbox/<int:user_id>', methods=['GET'])
@is_logged_in
def inboxchat(user_id):
    current_user_id = session['id']
    current = db.execute('SELECT * FROM users WHERE id = ?', user_id)[0]
    follows = db.execute('SELECT * FROM follows WHERE follower_id = ?', (session['id'],))
    senders = db.execute("SELECT users.id, users.username, m.content AS last_message, m.timestamp AS last_message_time, COUNT(CASE WHEN m.is_read = 0 AND m.receiver_id = ? THEN 1 END) AS unread_count FROM users JOIN messages m ON (users.id = m.sender_id OR users.id = m.receiver_id) WHERE (m.sender_id = ? OR m.receiver_id = ?) AND users.id != ? AND m.timestamp = (SELECT MAX(timestamp) FROM messages WHERE (sender_id = m.sender_id AND receiver_id = m.receiver_id) OR (sender_id = m.receiver_id AND receiver_id = m.sender_id)) GROUP BY users.id ORDER BY last_message_time DESC", session['id'], session['id'], session['id'], session['id'])

    for convo in senders:
        if len(convo['last_message']) > 25:
            convo['last_message'] = convo['last_message'][:25] + '...'

    # Retrieve conversation messages
    messages = db.execute(
        '''SELECT * FROM messages
           WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
           ORDER BY timestamp''',
        current_user_id, user_id, user_id, current_user_id
    )

    return render_template('inbox.html', get_unread=get_unread, follows=follows, current=current, senders=senders, messages=messages)

@app.route('/send_message/<int:id>', methods=['POST'])
@is_logged_in
def send_message(id):
    sender_id = session['id']  # Replace with the logged-in user's ID
    receiver_id = id
    content = request.form['content' '']
    file = request.files.get('file')
    if file:
        filename = str(uuid.uuid1())+os.path.splitext(file.filename)[1]
        file.save(os.path.join("static/uploads", filename))
        print(f'file saved at {filename}')

        # Save file and message to database
        db.execute('INSERT INTO messages (sender_id, receiver_id, content, file_url) VALUES (?, ?, ?, ?)',sender_id, receiver_id, content, filename)
        

    else:
        # Save message without file to database
        db.execute('INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)', sender_id, receiver_id, content)

    return redirect(request.referrer or url_for('inbox'))
    
@app.route('/del_message/<int:id>', methods=['POST'])
@is_logged_in
def del_message(id):
    db.execute("DELETE FROM messages WHERE id = ? ", id)
    return redirect(request.referrer or url_for('inbox'))

if __name__ == "__main__":
    app.secret_key= 'abdulhameedkhattab07'
    app.run(debug=True)