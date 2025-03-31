# tests/test_basic.py
def test_simple():
    """A simple test to verify pytest is working"""
    assert 1 + 1 == 2

def test_string_operations():
    """Test string operations"""
    assert "hello" + " world" == "hello world"
    assert "hello".upper() == "HELLO"