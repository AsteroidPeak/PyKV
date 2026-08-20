import pytest
from pykv.store import Store


def test_set_then_get():
    """Setting a key should make it retrievable."""
    store = Store()
    store.set("mom", "9876543210")
    assert store.get("mom") == "9876543210"


def test_delete_removes_key():
    """Deleting a key should remove it and return True."""
    store = Store()
    store.set("mom", "9876543210")
    result = store.delete("mom")
    assert result == True
    assert store.get("mom") is None


def test_delete_missing_key_returns_false():
    """Deleting a key that doesn't exist should return False."""
    store = Store()
    result = store.delete("nonexistent")
    assert result == False


def test_get_missing_key_returns_none():
    """
    Getting a key that doesn't exist should return None, not raise an error.
    This is a deliberate API choice: callers can check for None instead of
    catching KeyError, which makes error handling cleaner at the call site.
    """
    store = Store()
    assert store.get("nonexistent") is None


def test_overwrite_key():
    """Overwriting a key should update its value."""
    store = Store()
    store.set("name", "Alice")
    store.set("name", "Bob")
    assert store.get("name") == "Bob"