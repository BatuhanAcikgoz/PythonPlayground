# tests/mock_app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Create a Flask application for testing
mock_app = Flask(__name__)
mock_app.config['TESTING'] = True
mock_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
mock_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
mock_app.config['SECRET_KEY'] = 'test-secret-key'

# Initialize SQLAlchemy
mock_db = SQLAlchemy(mock_app)

# Create models for testing
class MockRole(mock_db.Model):
    id = mock_db.Column(mock_db.Integer, primary_key=True)
    name = mock_db.Column(mock_db.String(50), unique=True, nullable=False)
    description = mock_db.Column(mock_db.String(255))

# Many-to-many relationship table
mock_user_roles = mock_db.Table('mock_user_roles',
    mock_db.Column('user_id', mock_db.Integer, mock_db.ForeignKey('mock_user.id'), primary_key=True),
    mock_db.Column('role_id', mock_db.Integer, mock_db.ForeignKey('mock_role.id'), primary_key=True)
)

class MockUser(mock_db.Model):
    id = mock_db.Column(mock_db.Integer, primary_key=True)
    username = mock_db.Column(mock_db.String(100), unique=True, nullable=False)
    email = mock_db.Column(mock_db.String(120), unique=True)
    password_hash = mock_db.Column(mock_db.String(255))
    roles = mock_db.relationship('MockRole', secondary=mock_user_roles,
                            backref=mock_db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

    def is_admin(self):
        return self.has_role('admin')

    def is_teacher(self):
        return self.has_role('teacher') or self.is_admin()