import pytest
from app.events.event_definitions import EventType
from app.events.event_manager import EventManager


@pytest.fixture
def setup_event_manager():
    """Fixture to provide a fresh instance of EventManager."""
    manager = EventManager()
    yield manager


def test_register_single_handler(setup_event_manager):
    """Test that a single handler is registered successfully."""
    event_type = EventType.USER_REGISTERED

    def sample_handler(data):
        return "handler_called"

    setup_event_manager.register_handler(event_type, sample_handler)
    assert event_type in setup_event_manager._handlers
    assert sample_handler in setup_event_manager._handlers[event_type]


def test_register_multiple_handlers(setup_event_manager):
    """Test that multiple handlers can be registered for the same event type."""
    event_type = EventType.USER_LOGGED_IN

    def first_handler(data):
        return "first_handler_called"

    def second_handler(data):
        return "second_handler_called"

    setup_event_manager.register_handler(event_type, first_handler)
    setup_event_manager.register_handler(event_type, second_handler)

    assert len(setup_event_manager._handlers[event_type]) == 2
    assert first_handler in setup_event_manager._handlers[event_type]
    assert second_handler in setup_event_manager._handlers[event_type]


def test_handler_called_on_event_trigger(setup_event_manager, mocker):
    """Test that registered handlers are invoked when the event is triggered."""
    event_type = EventType.BOOKMARK_CREATED

    mock_handler = mocker.Mock()
    setup_event_manager.register_handler(event_type, mock_handler)
    setup_event_manager.trigger_event(event_type, {"data": "test"})

    mock_handler.assert_called_once_with({"data": "test"})


def test_register_handler_duplicates(setup_event_manager):
    """Test that registering the same handler multiple times does not duplicate entries."""
    event_type = EventType.USER_POINTS_UPDATED

    def sample_handler(data):
        return "called"

    setup_event_manager.register_handler(event_type, sample_handler)
    setup_event_manager.register_handler(event_type, sample_handler)

    assert len(setup_event_manager._handlers[event_type]) == 2
