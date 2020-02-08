import datetime
import os
from datetime import datetime, timedelta

from flask_sqlalchemy import SQLAlchemy
from flask_user import UserMixin, UserManager
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
photos = None

from random import randint


def random_integer():
    min_ = 1
    max_ = 255
    return randint(min_, max_)


def lessthenNow():
    return datetime.now() - timedelta(minutes=1)


class File(db.Model):
    id = db.Column(db.Integer(), primary_key=1)
    processed = db.Column(db.Boolean, nullable=False, default=False)
    description = db.Column(db.Text, nullable=True, default='')
    image = db.Column(db.String(256))
    updated_at = db.Column('updated_at', db.DateTime, default=lessthenNow, onupdate=datetime.now)
    height = db.Column(db.Integer, nullable=False, default=0)
    width = db.Column(db.Integer, nullable=False, default=0)


class ObjectClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, default='test')
    _r = db.Column(db.Integer, nullable=False, default=random_integer)
    _g = db.Column(db.Integer, nullable=False, default=random_integer)
    _b = db.Column(db.Integer, nullable=False, default=random_integer)
    description = db.Column(db.Text, nullable=True, default='')

    @property
    def b(self):
        return self._b

    @property
    def g(self):
        return self._g

    @property
    def r(self):
        return self._r


class User(db.Model, UserMixin):
    active = True
    confirmed_at = datetime.utcnow()
    id = db.Column(db.Integer, primary_key=True)
    roles = db.relationship('Role', secondary='user_roles',
                            backref=db.backref('users', lazy='dynamic'))
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    _password = db.Column(db.String(255), nullable=False, default='')

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, in_password):
        global user_manager
        self._password = generate_password_hash(in_password, method='SHA256')

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)


class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    # __str__ is required by Flask-Admin, so we can have human-readable values for the Role when editing a User.
    # If we were using Python 2.7, this would be __unicode__ instead.
    def __str__(self):
        return self.name

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)


class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))


user_manager = ''


def CreateWallDatabase(app):
    global user_manager
    db.init_app(app)
    db.create_all()
    user_manager = UserManager(app, db, User)

    # Create 'admin' and 'user'
    if not User.query.filter(User.email == 'admin@example.com').first():
        passwd = os.getenv('ADMIN_PASSWORD', 'got')

        user_admin = User(email='admin@example.com', username='admin', \
                          password=passwd)
        user_admin.roles.append(Role(name='admin'))
        user_admin.roles.append(Role(name='marker'))
        user_admin.roles.append(Role(name='uploader'))
        db.session.add(user_admin)

        db.session.commit()

    return db
