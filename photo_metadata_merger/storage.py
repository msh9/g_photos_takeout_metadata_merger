import json
import gzip
from pathlib import Path

class DuplicateKey(Exception):

    def __init__(self, hash: str, name: str):
        self.hash = hash
        self.name = name

class InMemory:
    """Defines an in-memory set for data depulication and name tracking"""

    def __init__(self):
        self._local = dict()

    def seen(self, hexHash: str) -> bool:
        return hexHash in self._local.keys()

    def add(self, hexHash: str, location: Path):
        if not hexHash in self._local:
            self._local[hexHash] = location
        else:
            raise DuplicateKey(hexHash, str(location))

class Persisted(InMemory):
    """Adds file system persistence to InMemory by supporting export to compressed JSON"""

    @staticmethod
    def _load_from_file(on_disk: Path) -> dict[str, str]:
        with gzip.open(on_disk, 'rt') as f:
            data = json.load(f)
        return data

    def __init__(self, on_disk: Path):
        super().__init__()
        self._persistance_path = on_disk
        if on_disk.exists():
            existing_stored = self._load_from_file(on_disk)
            self._local |= existing_stored

    def save(self):
        with gzip.open(self._persistance_path, 'wt') as f:
            json.dump(self._local, f)