import hashlib
from datetime import datetime
from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin

from werkzeug.security import generate_password_hash, check_password_hash
from quickchat.extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    nickname = db.Column(db.String(30))
    password_hash = db.Column(db.String(128))
    email_hash = db.Column(db.String(128))
    github = db.Column(db.String(255))
    website = db.Column(db.String(255))
    bio = db.Column(db.String(120))
    messages = db.relationship('Message', back_populates='author', cascade='all')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.generate_email_hash()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        # print("password_hash", generate_password_hash(password))

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_email_hash(self):
        if self.email is not None and self.email_hash is None:
            self.email_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

    @property
    def is_admin(self):
        return self.email == current_app.config['ADMIN_EMAIL']

    @property
    def gravatar(self):
        return url_for('static', filename='logo.png')
        # return 'https://gravatar.com/avatar/%s?d=monsterid' % self.email_hash


class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', back_populates='messages')


class Guest(AnonymousUserMixin):
    @property
    def is_admin(self):
        return False


login_manager.anonymous_user = Guest

