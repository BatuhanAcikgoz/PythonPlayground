# tests/test_routes.py
import pytest
from tests.mock_app import create_mock_app  # Use factory function instead of global instance

@pytest.fixture
def routes_app():
    # Create a fresh app instance for each test
    app = create_mock_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'

    # Add routes for testing BEFORE any requests are made
    @app.route('/')
    def index():
        return 'Home Page'

    @app.route('/protected')
    def protected():
        return 'Protected Content'

    @app.route('/admin-only')
    def admin_only():
        return 'Admin Only'

    with app.app_context():
        app.db.create_all()
        yield app
        app.db.drop_all()

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