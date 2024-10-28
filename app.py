import os

from cs50 import SQL
from flask import Flask, flash, redirect, url_for, render_template, request, session, jsonify
from flask import session, request, Flask, flash, redirect, url_for, session, logging, render_template, send_from_directory
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, valid_email

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
def home():
    return render_template("home.html")