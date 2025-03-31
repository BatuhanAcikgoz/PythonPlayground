# tests/test_app.py
import pytest

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200

def test_login_success(client):
    response = client.post(
        '/login',
        data={'username': 'testadmin', 'password': 'password'},
        follow_redirects=True
    )
    assert response.status_code == 200
    # Check for something that indicates successful login
    assert b'logout' in response.data.lower() or b'admin' in response.data.lower()

def test_admin_access(auth_client):
    response = auth_client.get('/admin')
    assert response.status_code == 200