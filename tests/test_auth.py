# tests/test_auth.py
import pytest
from tests.mock_app import mock_app, MockUser, mock_db
from flask import session
from flask_login import login_user, logout_user, current_user


class FlaskLoginMock:
    is_authenticated = False

    def __init__(self, user_id=None):
        self.user_id = user_id

    def get_id(self):
        return self.user_id


@pytest.fixture
def auth_app():
    mock_app.config['LOGIN_DISABLED'] = False
    mock_app.config['SECRET_KEY'] = 'test_secret_key'
    mock_app.testing = True

    with mock_app.app_context():
        mock_db.create_all()

        # Create a test user
        user = MockUser(username='testuser', email='test@example.com')
        user.set_password('password')
        mock_db.session.add(user)
        mock_db.session.commit()

        yield mock_app

        mock_db.session.remove()
        mock_db.drop_all()


@pytest.fixture
def client(auth_app):
    return auth_app.test_client()


def test_password_validation():
    user = MockUser(username='passtest', email='pass@example.com')
    user.set_password('securepass')

    assert user.check_password('securepass')
    assert not user.check_password('wrongpass')


def test_login_route(client):
    # Add a login route to mock_app for testing
    @mock_app.route('/login_test', methods=['POST'])
    def login_test():
        username = 'testuser'
        user = MockUser.query.filter_by(username=username).first()
        if user and user.check_password('password'):
            login_mock = FlaskLoginMock(user.id)
            session['user_id'] = user.id
            return 'Login successful'
        return 'Login failed'

    response = client.post('/login_test')
    assert response.status_code == 200
    assert b'Login successful' in response.data


def test_user_creation():
    user = MockUser(username='newuser', email='new@example.com')
    user.set_password('newpassword')

    assert user.username == 'newuser'
    assert user.email == 'new@example.com'
    assert user.check_password('newpassword')