import pytest
from pykv.store import Store

def test_kill_and_restart(tmp_path):
    """Create 100 keys, then restart Store and verify all are recovered.

    Uses a temporary WAL file so the production wal.log is untouched.
    """
    wal_path = tmp_path / "wal.log"

    # First Store instance writes 100 entries.
    store_a = Store(wal_path=wal_path)
    for i in range(100):
        store_a.set(f"key{i}", f"value{i}")

    # Simulate a fresh process by creating a new Store that reads the same WAL.
    store_b = Store(wal_path=wal_path)

    # Verify each key/value pair is present.
    for i in range(100):
        assert store_b.get(f"key{i}") == f"value{i}"
    # Also verify the full key list matches.
    assert set(store_b.keys()) == {f"key{i}" for i in range(100)}

