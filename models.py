from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from typing import List

db = SQLAlchemy()

class Role:
    ADMIN = "admin"
    PUBLISHER = "publisher"
    READER = "reader"

ROLE_PERMISSIONS = {
    Role.ADMIN: [
        "read:module",
        "upload:module",
        "delete:module",
        "manage:users",
        "generate:module"
    ],
    Role.PUBLISHER: [
        "read:module",
        "upload:module",
        "generate:module"
    ],
    Role.READER: [
        "read:module"
    ]
}

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))  # Increased length to accommodate scrypt hash
    token = db.Column(db.String(500))
    role = db.Column(db.String(20), default=Role.READER)
    repositories = db.relationship('Repository', backref='owner', lazy=True)
    namespaces = db.Column(db.JSON, default=list)
    _permissions = db.Column('permissions', db.JSON, default=list)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def permissions(self) -> List[str]:
        if self._permissions is None:
            self._permissions = ROLE_PERMISSIONS.get(self.role, ROLE_PERMISSIONS[Role.READER])
        return self._permissions

    @permissions.setter
    def permissions(self, value):
        self._permissions = value

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'namespaces': self.namespaces or [],
            'permissions': self.permissions or []
        }

class Repository(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    namespace = db.Column(db.String(120))
    name = db.Column(db.String(120))
    provider = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Repository {self.url}>'