from . import db
from flask_login import UserMixin
from sqlalchemy import func
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50))
    username = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    profile_picture = db.Column(db.String(255), nullable=True)

    def __init__(self, role, email, username, password, profile_picture):
        self.role = role
        self.email = email
        self.username = username
        self.password = password
        self.profile_picture = profile_picture

class Discussion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='discussions')
    messages = db.relationship('Message', backref='discussion', lazy=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, title, user_id):
        self.title = title
        self.user_id = user_id

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='message')
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'), nullable=False)

    def __init__(self, text, user_id, discussion_id):
        self.text = text
        self.user_id = user_id
        self.discussion_id = discussion_id

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    anime_title = db.Column(db.String, nullable=False)
    text = db.Column(db.Text, nullable=False)

    def __init__(self, user_id, anime_title, text):
        self.user_id = user_id
        self.anime_title = anime_title
        self.text = text