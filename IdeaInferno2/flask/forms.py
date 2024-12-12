
from wtforms import Form, RadioField, FileField, SelectField, StringField, TextAreaField, PasswordField, validators
from werkzeug.utils import secure_filename
from flask_wtf.file import FileAllowed
import requests
import re

def extract_usernames(text):
    return re.findall(r'@(\w+)', text)

def link_usernames(content):
    return re.sub(r'@w+', r'<a href="/profile/\1">@\1</a>', content)


#register form class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50), validators.DataRequired()])
    username = StringField('Username', [validators.Length(min=4, max=25), validators.DataRequired()])
    country = StringField('Country', [validators.DataRequired()])
    email = StringField('Email', [validators.Length(min=6, max=50), validators.DataRequired()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
    type =  SelectField('Preference', choices=['Web dev', 'App Dev', 'Game Dev'])

class EditForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    blog = StringField('Blog Name', [validators.Length(min=3, max=20)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    bio = TextAreaField('Bio', [validators.Length(min=10)])
    confirm = PasswordField('Confirm Password')
    type =  RadioField('Account Type', choices=['Blogger', 'User'])

#article form class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200), validators.DataRequired()])
    body = TextAreaField('Body', [validators.Length(min=20), validators.DataRequired()])
    category =  RadioField('Category', choices=['Web Dev', 'AI', 'App Dev', 'Game Dev'])
    anonymous =  RadioField('Post Anonymously', choices=['yes', 'no'])