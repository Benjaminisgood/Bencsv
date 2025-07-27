# auth/models.py
from flask_login import UserMixin
from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(64), unique=True, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.id} {self.username}>'