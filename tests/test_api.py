# tests/test_api.py
import json

import pytest
from app.routes.api import proxy
from tests.mock_app import create_mock_app


@pytest.fixture
def api_app():
    mock_app = create_mock_app()
    db = mock_app.db
    MockUser = mock_app.MockUser
    MockRole = mock_app.MockRole

    # Define ALL routes at the beginning
    @mock_app.route('/api/test/users')
    def test_users_api():
        users = MockUser.query.all()
        return json.dumps([{
            'id': user.id,
            'username': user.username,
            'email': user.email
        } for user in users])

    @mock_app.route('/api/test/admin-check/<username>')
    def test_admin_check(username):
        user = MockUser.query.filter_by(username=username).first()
        if not user:
            return json.dumps({'error': 'User not found'}), 404
        return json.dumps({'is_admin': user.is_admin()})

    with mock_app.app_context():
        db.create_all()
        # Create test users
        user1 = MockUser(username='api_user1', email='api1@example.com')
        user1.set_password('password')
        user2 = MockUser(username='api_user2', email='api2@example.com')
        user2.set_password('password')
        db.session.add_all([user1, user2])
        db.session.commit()

        yield mock_app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(api_app):
    return api_app.test_client()


def test_users_api(client):
    response = client.get('/api/test/users')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) >= 2
    assert 'username' in data[0]
    assert 'email' in data[0]


def test_user_roles_api(api_app, client):
    db = api_app.db
    MockUser = api_app.MockUser
    MockRole = api_app.MockRole

    with api_app.app_context():
        # Create roles
        admin_role = MockRole(name='admin', description='Admin role')
        db.session.add(admin_role)
        # Create admin user
        admin = MockUser(username='api_admin', email='apiadmin@example.com')
        admin.set_password('adminpass')
        admin.roles.append(admin_role)
        db.session.add(admin)
        db.session.commit()

    response = client.get('/api/test/admin-check/api_admin')
    data = json.loads(response.data)
    assert data['is_admin'] is True

    response = client.get('/api/test/admin-check/api_user1')
    data = json.loads(response.data)
    assert data['is_admin'] is False


def test_admin_required_with_admin_user(api_app, client, mocker):
    mocker.patch('flask_login.utils._get_user', return_value=mocker.Mock(is_authenticated=True, is_admin=lambda: True))

    @api_app.route('/api/test/admin-endpoint')
    @api_app.admin_decorator
    def test_admin_endpoint():
        return json.dumps({"success": True})

    response = client.get('/api/test/admin-endpoint')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True


def test_admin_required_with_non_admin_user(api_app, client, mocker):
    mocker.patch('flask_login.utils._get_user', return_value=mocker.Mock(is_authenticated=True, is_admin=lambda: False))

    @api_app.route('/api/test/admin-endpoint')
    @api_app.admin_decorator
    def test_admin_endpoint():
        return json.dumps({"success": True})

    response = client.get('/api/test/admin-endpoint')
    assert response.status_code == 403
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Admin yetkisi gerekiyor"


def test_proxy_get(client, mocker):
    mocker.patch('requests.get', return_value=mocker.Mock(status_code=200, json=lambda: {"data": "success"}))

    response = client.get('/api/test/proxy-endpoint')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["data"] == "success"


def test_proxy_post(client, mocker):
    mocker.patch('requests.post', return_value=mocker.Mock(status_code=201, json=lambda: {"result": "created"}))

    response = client.post('/api/test/proxy-endpoint', json={"key": "value"})
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["result"] == "created"