# tests/test_models_advanced.py
import sys
import os
import pytest
import uuid
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.mock_app import mock_app, mock_db


# Create models for testing without importing from app
class MockRole(mock_db.Model):
    id = mock_db.Column(mock_db.Integer, primary_key=True)
    name = mock_db.Column(mock_db.String(50), unique=True, nullable=False)
    description = mock_db.Column(mock_db.String(255))


mock_user_roles = mock_db.Table('mock_user_roles',
                                mock_db.Column('user_id', mock_db.Integer, mock_db.ForeignKey('mock_user.id'),
                                               primary_key=True),
                                mock_db.Column('role_id', mock_db.Integer, mock_db.ForeignKey('mock_role.id'),
                                               primary_key=True)
                                )


class MockUser(mock_db.Model):
    id = mock_db.Column(mock_db.Integer, primary_key=True)
    username = mock_db.Column(mock_db.String(100), unique=True, nullable=False)
    email = mock_db.Column(mock_db.String(120), unique=True, nullable=False)
    password_hash = mock_db.Column(mock_db.String(255), nullable=False)
    created_at = mock_db.Column(mock_db.DateTime, default=datetime.utcnow)
    roles = mock_db.relationship('MockRole', secondary=mock_user_roles,
                                 backref=mock_db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

    def is_admin(self):
        return self.has_role('admin')

    def is_teacher(self):
        return self.has_role('teacher') or self.is_admin()


@pytest.fixture
def setup_db():
    with mock_app.app_context():
        mock_db.create_all()

        # Create roles
        admin_role = MockRole(name='admin', description='Admin role')
        teacher_role = MockRole(name='teacher', description='Teacher role')
        student_role = MockRole(name='student', description='Student role')
        mock_db.session.add_all([admin_role, teacher_role, student_role])
        mock_db.session.commit()

        yield

        mock_db.session.remove()
        mock_db.drop_all()


def test_user_roles(setup_db):
    with mock_app.app_context():
        # Get roles
        admin_role = MockRole.query.filter_by(name='admin').first()
        teacher_role = MockRole.query.filter_by(name='teacher').first()
        student_role = MockRole.query.filter_by(name='student').first()

        # Create users with roles
        admin_user = MockUser(username='admin_test', email='admin@test.com')
        admin_user.set_password('password123')
        admin_user.roles.append(admin_role)

        teacher_user = MockUser(username='teacher_test', email='teacher@test.com')
        teacher_user.set_password('password123')
        teacher_user.roles.append(teacher_role)

        student_user = MockUser(username='student_test', email='student@test.com')
        student_user.set_password('password123')
        student_user.roles.append(student_role)

        mock_db.session.add_all([admin_user, teacher_user, student_user])
        mock_db.session.commit()

        # Test role checks
        assert admin_user.has_role('admin')
        assert admin_user.is_admin()
        assert admin_user.is_teacher()

        assert teacher_user.has_role('teacher')
        assert not teacher_user.is_admin()
        assert teacher_user.is_teacher()

        assert student_user.has_role('student')
        assert not student_user.is_admin()
        assert not student_user.is_teacher()