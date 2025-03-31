# tests/mock_app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


def create_mock_app():
    """Factory function to create a fresh Flask application for testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'

    db = SQLAlchemy(app)

    class MockRole(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50), unique=True, nullable=False)
        description = db.Column(db.String(255))

    mock_user_roles = db.Table('mock_user_roles',
                               db.Column('user_id', db.Integer, db.ForeignKey('mock_user.id'), primary_key=True),
                               db.Column('role_id', db.Integer, db.ForeignKey('mock_role.id'), primary_key=True)
                               )

    class MockUser(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(100), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        roles = db.relationship('MockRole', secondary=mock_user_roles,
                                backref=db.backref('users', lazy='dynamic'))

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

    # Store models in app for access
    app.MockUser = MockUser
    app.MockRole = MockRole
    app.db = db

    return app


# Maintain backward compatibility
mock_app = create_mock_app()
mock_db = mock_app.db
MockUser = mock_app.MockUser
MockRole = mock_app.MockRole