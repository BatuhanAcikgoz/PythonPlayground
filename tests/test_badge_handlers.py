from unittest.mock import MagicMock, patch

import pytest
from app.events.badge_handlers import handle_question_solved
from app.models.badge_criteria import BadgeCriteria
from app.models.user import User
from app.models.user_badges import UserBadge


@pytest.fixture
def mock_event_data():
    return {"user_id": 1, "question_id": 101}


@pytest.fixture
def mock_user():
    user = User(id=1, username="test_user", email="test@test.com", points=100)
    return user


def test_handle_question_solved_with_valid_data(mock_event_data, mock_user):
    with patch("app.events.badge_handlers.db.session") as mock_db_session, \
            patch("app.events.badge_handlers.User.query.get") as mock_user_query, \
            patch("app.events.badge_handlers.db.session.execute") as mock_execute, \
            patch("app.events.badge_handlers.BadgeCriteria.query.filter_by") as mock_filter_by, \
            patch("app.events.badge_handlers.event_manager.trigger_event") as mock_trigger_event:
        mock_user_query.return_value = mock_user
        mock_execute.side_effect = [
            MagicMock(first=MagicMock(return_value=MagicMock(point_value=50))),
            MagicMock(first=MagicMock(return_value=MagicMock(solved_count=5))),
        ]
        mock_filter_by.return_value.all.return_value = []

        handle_question_solved(mock_event_data)

        mock_db_session.add.assert_called_once_with(mock_user)
        mock_trigger_event.assert_called_once_with("USER_POINTS_UPDATED", {"user_id": 1, "points": 150})
        mock_db_session.commit.assert_called_once()


def test_handle_question_solved_with_missing_user_id(mock_event_data):
    mock_event_data["user_id"] = None

    with patch("app.events.badge_handlers.current_app.logger.warning") as mock_logger_warning:
        handle_question_solved(mock_event_data)
        mock_logger_warning.assert_called_once_with("Eksik veri: user_id=None, question_id=101")


def test_handle_question_solved_with_missing_question_id(mock_event_data):
    mock_event_data["question_id"] = None

    with patch("app.events.badge_handlers.current_app.logger.warning") as mock_logger_warning:
        handle_question_solved(mock_event_data)
        mock_logger_warning.assert_called_once_with("Eksik veri: user_id=1, question_id=None")


def test_handle_question_solved_with_existing_badge(mock_event_data, mock_user):
    with patch("app.events.badge_handlers.db.session") as mock_db_session, \
            patch("app.events.badge_handlers.User.query.get") as mock_user_query, \
            patch("app.events.badge_handlers.db.session.execute") as mock_execute, \
            patch("app.events.badge_handlers.BadgeCriteria.query.filter_by") as mock_filter_by, \
            patch("app.events.badge_handlers.UserBadge.query.filter_by") as mock_badge_filter_by:
        mock_user_query.return_value = mock_user
        mock_execute.side_effect = [
            MagicMock(first=MagicMock(return_value=MagicMock(point_value=50))),
            MagicMock(first=MagicMock(return_value=MagicMock(solved_count=5))),
        ]
        mock_filter_by.return_value.all.return_value = [
            BadgeCriteria(id=1, badge_id=1, criteria_type="question_solved", criteria_value="101")
        ]
        mock_badge_filter_by.return_value.first.return_value = UserBadge(user_id=1, badge_id=1)

        handle_question_solved(mock_event_data)

        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_called_once()
