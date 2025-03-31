# tests/mock_app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

mock_app = Flask(__name__)
mock_app.config['TESTING'] = True
mock_app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
mock_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
mock_app.config['SECRET_KEY'] = 'test-key'

mock_db = SQLAlchemy(mock_app)


class MockUser(mock_db.Model):
    id = mock_db.Column(mock_db.Integer, primary_key=True)
    username = mock_db.Column(mock_db.String(100), unique=True, nullable=False)
    password_hash = mock_db.Column(mock_db.String(255), nullable=False)

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)


with mock_app.app_context():
    mock_db.create_all()