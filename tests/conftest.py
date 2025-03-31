# tests/conftest.py
import pytest
from tests.mock_app import create_mock_app

@pytest.fixture
def app():
    mock_app = create_mock_app()
    db = mock_app.db
    MockUser = mock_app.MockUser

    with mock_app.app_context():
        db.create_all()

        # Create test user
        test_user = MockUser(username='testuser', email='test@example.com')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()

        yield mock_app

        # Clean up
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()