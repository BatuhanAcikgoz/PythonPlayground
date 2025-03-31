# tests/test_models_advanced.py
import pytest
from tests.mock_app import mock_app, mock_db, MockRole, MockUser

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