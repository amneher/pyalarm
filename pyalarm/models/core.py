import uuid
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id: int = db.Column(db.String(), primary_key=True, default=str(uuid.uuid4()))
    username: str = db.Column(db.String())
    email: str = db.Column(db.String())
    location_ids: str = db.Column(db.String())
    active: bool = db.Column(db.Boolean(), default=True)
    pwd_hash: str = db.Column(db.String())

    def __init__(self, username: str, email: str, pwd_hash: str):
        self.username = username
        self.email = email
        self.pwd_hash = pwd_hash

    def __repr__(self):
        return f'User: {self.username} ID: {self.id}'


def add_user(username: str, email: str, password: str):
    if not User.query.filter_by(username=username).first():
        user = User(username=username, email=email, pwd_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return user.username
    else:
        user = User.query.filter_by(username=username).first()
        return user.username
