import os
import json
import time
from pathlib import Path
from typing import Any, Optional

class Store:
    DEFAULT_WAL_PATH = Path(os.path.join(os.path.dirname(__file__), "..", "wal.log"))

    def __init__(self, wal_path: Optional[os.PathLike] = None):
        self._wal_path = Path(wal_path) if wal_path is not None else self.DEFAULT_WAL_PATH
        self.data: dict = {}
        self._replay_wal()

    def contains(self, key: str) -> bool:
        return key in self.data

    def _write_wal(self, entry: dict) -> None:
        line = json.dumps(entry)
        os.makedirs(self._wal_path.parent, exist_ok=True)
        with open(self._wal_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
            f.flush()
            os.fsync(f.fileno())

    def _replay_wal(self) -> None:
        if not self._wal_path.is_file():
            return
        with open(self._wal_path, "r", encoding="utf-8") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    entry = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                op = entry.get("op")
                if op == "SET":
                    self.data[entry["key"]] = entry["value"]
                elif op == "DEL":
                    self.data.pop(entry["key"], None)

    def set(self, key: str, value: Any) -> None:
        entry = {"op": "SET", "key": key, "value": value, "ts": time.time()}
        self._write_wal(entry)
        self.data[key] = value

    def get(self, key: str) -> Any:
        return self.data.get(key)

    def delete(self, key: str) -> bool:
        if key in self.data:
            entry = {"op": "DEL", "key": key, "ts": time.time()}
            self._write_wal(entry)
            del self.data[key]
            return True
        return False

    def keys(self) -> list:
        return list(self.data.keys())
