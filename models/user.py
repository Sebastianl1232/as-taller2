"""
Modelo User - Representa un usuario autenticado en la aplicación
"""

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db


class User(UserMixin, db.Model):
    """Modelo para usuarios del sistema"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    task_owners = db.relationship(
        'TaskOwner',
        back_populates='user',
        cascade='all, delete-orphan'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class TaskOwner(db.Model):
    """Asocia cada tarea a un único usuario propietario"""

    __tablename__ = 'task_owners'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False, unique=True)

    user = db.relationship('User', back_populates='task_owners')
    task = db.relationship('Task', back_populates='owner_link')
