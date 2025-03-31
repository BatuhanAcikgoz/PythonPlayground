# tests/test_models.py
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from werkzeug.security import generate_password_hash, check_password_hash


def test_password_hash():
    """Test password hashing works correctly"""
    password = "secure_password"
    hashed = generate_password_hash(password)

    assert hashed != password
    assert check_password_hash(hashed, password) is True
    assert check_password_hash(hashed, "wrong_password") is False