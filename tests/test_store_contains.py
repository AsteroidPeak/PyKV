import pytest
from pykv.store import Store


def test_contains_existing_key():
    store = Store()
    store.set('a', 1)
    assert store.contains('a') is True


def test_contains_missing_key():
    store = Store()
    assert store.contains('missing') is False


def test_contains_key_with_none():
    store = Store()
    store.set('null', None)
    assert store.contains('null') is True
    # get should return None but contains is True
    assert store.get('null') is None

