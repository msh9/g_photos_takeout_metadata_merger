import json
import gzip
import hashlib
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

    def seen_content_bytes(self, content: bytes) -> bool:
        return self.seen(self._hash(content))

    def add(self, hexHash: str, location: Path):
        if hexHash not in self._local:
            self._local[hexHash] = str(location)
        else:
            raise DuplicateKey(hexHash, str(location))

    def add_content_bytes(self, content: bytes, location: Path):
        return self.add(self._hash(content), location)

    def _hash(self, content: bytes) -> str:
        file_hash = hashlib.sha1(content, usedforsecurity=False)
        return file_hash.hexdigest()


class Persisted(InMemory):
    """Adds file system persistence to InMemory by supporting export to compressed JSON"""

    @staticmethod
    def _load_from_file(on_disk: Path) -> dict[str, str]:
        with gzip.open(on_disk, "rt") as f:
            data = json.load(f)
        return data

    def __init__(self, on_disk: Path):
        super().__init__()
        self._persistance_path = on_disk
        if on_disk.exists():
            existing_stored = self._load_from_file(on_disk)
            self._local |= existing_stored

    def save(self):
        with gzip.open(self._persistance_path, "wt") as f:
            json.dump(self._local, f)
