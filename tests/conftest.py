# tests/conftest.py
import os
import sys
import pytest

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import from app
from app import app as flask_app, db, Role, User


@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })

    with flask_app.app_context():
        db.create_all()
        # Create test roles
        student_role = Role(name='student', description='Student role')
        teacher_role = Role(name='teacher', description='Teacher role')
        admin_role = Role(name='admin', description='Admin role')
        db.session.add_all([student_role, teacher_role, admin_role])

        # Create test users
        test_admin = User(username='testadmin', email='admin@test.com')
        test_admin.set_password('password')
        test_admin.roles.append(admin_role)

        test_student = User(username='teststudent', email='student@test.com')
        test_student.set_password('password')
        test_student.roles.append(student_role)

        db.session.add_all([test_admin, test_student])
        db.session.commit()

    yield flask_app

    # Clean up after test is complete
    with flask_app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    client.post('/login', data={'username': 'testadmin', 'password': 'password'})
    return client