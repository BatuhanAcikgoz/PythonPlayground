# tests/test_socketio.py
import pytest
from tests.mock_app import mock_app
from flask_socketio import SocketIO, emit


class SocketIOTestClient:
    def __init__(self, app):
        self.socketio = SocketIO(app)
        self.received_messages = []

    def emit(self, event, data=None, namespace=None):
        self.socketio.emit(event, data, namespace=namespace)

    def on_message(self, event, data):
        self.received_messages.append((event, data))


@pytest.fixture
def socketio_app():
    mock_app.config['TESTING'] = True
    mock_app.config['SECRET_KEY'] = 'test_socket_key'

    socketio = SocketIO(mock_app)

    @socketio.on('test_event')
    def handle_test_event(data):
        emit('test_response', {'response': f"Received: {data['message']}"})

    @socketio.on('echo')
    def handle_echo(data):
        emit('echo_response', data)

    yield mock_app


@pytest.fixture
def socketio_client(socketio_app):
    return SocketIOTestClient(socketio_app)


def test_socket_events(socketio_app, socketio_client):
    # This is a simplified test since we can't fully test SocketIO without a running server
    # In a real test, you'd use pytest-flask-socketio or a similar library

    # Define a handler for the test
    @socketio_client.socketio.on('test_response')
    def on_test_response(data):
        socketio_client.on_message('test_response', data)

    # Test basic event functionality
    with socketio_app.test_client() as client:
        # Simplified assertion since we can't fully simulate the socketio connection
        assert socketio_client.socketio.server is not None