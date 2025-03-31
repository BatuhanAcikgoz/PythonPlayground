# tests/conftest.py
import pytest
from tests.mock_app import mock_app, mock_db, MockUser


@pytest.fixture
def app():
    with mock_app.app_context():
        mock_db.create_all()

        # Create test user
        test_user = MockUser(username='testuser')
        test_user.set_password('password')
        mock_db.session.add(test_user)
        mock_db.session.commit()

        yield mock_app

        # Clean up
        mock_db.session.remove()
        mock_db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()