import pytest
from app.events.handlers import notebook_summary_viewed_handler
from tests.mock_app import mock_app, mock_db


@pytest.fixture
def valid_data():
    return {"username": "test_user", "notebook_id": 12345}


@pytest.fixture
def missing_username():
    return {"notebook_id": 12345}


@pytest.fixture
def missing_notebook_id():
    return {"username": "test_user"}


@pytest.fixture
def empty_data():
    return {}


def test_notebook_summary_viewed_handler_valid_data(valid_data, caplog):
    with mock_app.app_context():
        notebook_summary_viewed_handler(valid_data)
        assert "test_user kullanıcısı 12345 numaralı not defterinin özetini görüntüledi" in caplog.text


def test_notebook_summary_viewed_handler_missing_username(missing_username, caplog):
    with mock_app.app_context():
        notebook_summary_viewed_handler(missing_username)
        assert "bilinmeyen kullanıcısı 12345 numaralı not defterinin özetini görüntüledi" in caplog.text


def test_notebook_summary_viewed_handler_missing_notebook_id(missing_notebook_id, caplog):
    with mock_app.app_context():
        notebook_summary_viewed_handler(missing_notebook_id)
        assert "test_user kullanıcısı bilinmeyen numaralı not defterinin özetini görüntüledi" in caplog.text


def test_notebook_summary_viewed_handler_empty_data(empty_data, caplog):
    with mock_app.app_context():
        notebook_summary_viewed_handler(empty_data)
        assert "bilinmeyen kullanıcısı bilinmeyen numaralı not defterinin özetini görüntüledi" in caplog.text
