# tests/test_models.py
import pytest
from app import User, Role, Course, Question

def test_user_password(app):
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        assert user.check_password('password123')
        assert not user.check_password('wrongpassword')

def test_user_roles(app):
    with app.app_context():
        admin = User.query.filter_by(username='testadmin').first()
        assert admin.has_role('admin')
        assert admin.is_admin()
        assert admin.is_teacher()

        student = User.query.filter_by(username='teststudent').first()
        assert student.has_role('student')
        assert not student.is_admin()
        assert not student.is_teacher()