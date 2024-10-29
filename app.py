import os
import uuid
from cs50 import SQL
from flask import Flask, flash, redirect, url_for, render_template, request, session, jsonify
from flask import session, request, Flask, flash, redirect, url_for, session, logging, render_template, send_from_directory
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from forms import RegisterForm, ArticleForm, EditForm, extract_usernames

from helpers import login_required, valid_email, is_logged_in

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower in app.config['ALLOWED_EXTENSIONS']

#confiq  Database
db = SQL("sqlite:///idea.db")

#static file path
@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/vision")
def vision():
    return render_template("vision.html")

#register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
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
            return redirect(url_for('register'))
        elif db_email_check:
            flash('Email Already Taken', 'danger')
            return redirect(url_for('register'))
        elif not prefernce:
            flash('Must Select a preference', 'danger')
            return redirect(url_for('register'))
        
        # Set db
        db.execute("INSERT INTO users (name, email, username, password, preference, country) VALUES(?, ?, ?, ?, ?, ?)", name, email, username, password, prefernce, country)

        #flash
        flash('You are Now Registered and can log in', 'success')

        #redirect to home
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
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
            error = 'Username Does Not Exist'
            return render_template('login.html', error=error)
        #compare passwords
        if not check_password_hash(result[0]['password'], password_candidate): 
            error = 'Invalid login'
            return render_template('login.html', error=error)
        else:
            session['logged_in'] = True
            session['username'] = username
            session['id'] = result[0]['id']
            session['email'] = result[0]['email']

            flash('You are now logged in', 'success')
            return redirect(url_for('home'))
    return render_template('login.html')

#logout
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
    flash("Successfully Logged Out")
    # Redirect user to login form
    return redirect("/")

@app.route("/home")
@is_logged_in
def home():
    posts = db.execute("SELECT * FROM posts")
    return render_template('home.html', posts=posts)

#add post
@app.route('/add_post', methods=['GET', 'POST'])
@is_logged_in
def add_post():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        
        title = form.title.data
        body = form.body.data
        category = form.category.data
        anonymous = form.anonymous.data
        image = request.files['image']
        if image:
            filename = str(uuid.uuid1())+os.path.splitext(image.filename)[1]
            image.save(os.path.join("static/uploads", filename))
        else:
            filename = None
        
        if anonymous == 'yes':
            isanonymous = 1
        else:
            isanonymous = 0

        db.execute("INSERT INTO posts (title, body, file_path, user_id, author, category, is_anonymous) VALUES(?, ?, ?, ?, ?, ?, ?)", title, body, filename, session['id'], session['username'], category, isanonymous)
        flash('Posted', 'success')

        return redirect(url_for('home'))
        
    return render_template('add_post.html', form=form)

if __name__ == "__main__":
    app.secret_key= 'abdulhameedkhattab07'
    app.run(debug=True)