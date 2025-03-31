# tests/test_app.py
import pytest

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Python' in response.data

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200

def test_login_success(client):
    response = client.post('/login', 
                           data={'username': 'testadmin', 'password': 'password'}, 
                           follow_redirects=True)
    assert response.status_code == 200
    assert b'logout' in response.data.lower()

def test_admin_panel_access(auth_client):
    response = auth_client.get('/admin')
    assert response.status_code == 200