# tests/test_routes.py
import pytest
from tests.mock_app import mock_app, mock_db, MockUser, MockRole


@pytest.fixture
def routes_app():
    mock_app.config['TESTING'] = True
    mock_app.config['SECRET_KEY'] = 'test_secret_key'

    # Add routes for testing
    @mock_app.route('/')
    def index():
        return 'Home Page'

    @mock_app.route('/protected')
    def protected():
        return 'Protected Content'

    @mock_app.route('/admin-only')
    def admin_only():
        return 'Admin Only'

    with mock_app.app_context():
        mock_db.create_all()
        yield mock_app
        mock_db.drop_all()


@pytest.fixture
def client(routes_app):
    return routes_app.test_client()


def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Home Page' in response.data


def test_protected_route(client):
    response = client.get('/protected')
    assert response.status_code == 200
    assert b'Protected Content' in response.data


def test_admin_route(client):
    response = client.get('/admin-only')
    assert response.status_code == 200
    assert b'Admin Only' in response.data


def test_nonexistent_route(client):
    response = client.get('/nonexistent')
    assert response.status_code == 404