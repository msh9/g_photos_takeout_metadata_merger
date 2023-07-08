import unittest
from pathlib import Path
import tests.constants as constants
import tempfile
from photo_metadata_merger.storage import InMemory, DuplicateKey, Persisted


class TestInMemory(unittest.TestCase):
    def setUp(self):
        self.inmemory = InMemory()

    def test_empty_state(self):
        hexHash = "abcd1234"
        self.assertFalse(self.inmemory.seen(hexHash))

    def test_added_reports_as_seen(self):
        hexHash = "abcd1234"
        location = Path("/path/to/file")

        self.inmemory.add(hexHash, location)
        self.assertTrue(
            self.inmemory.seen(hexHash)
        )  # hexHash should be seen after adding it

    def test_added_bytes_reports_as_seen(self):
        data = b"12345abcedef"
        self.inmemory.add_content_bytes(data, "foo/bar")
        self.assertTrue(self.inmemory.seen_content_bytes(data))

    def test_duplicate_key_raises_error(self):
        hexHash = "abcd1234"
        location1 = Path("/path/to/file1")
        location2 = Path("/path/to/file2")

        self.inmemory.add(hexHash, location1)
        with self.assertRaises(DuplicateKey) as context:
            self.inmemory.add(hexHash, location2)

        self.assertEqual(context.exception.hash, hexHash)
        self.assertEqual(context.exception.name, str(location2))


class TestPersisted(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.persisted_from_disk = Persisted(constants.get_persisted_hash_fixture_path())
        cls.test_directory = tempfile.TemporaryDirectory()

    def test_load_from_disk(self):
        self.assertTrue(TestPersisted.persisted_from_disk.seen("123"))

    def test_save_to_disk(self):
        save_to = Path(TestPersisted.test_directory.name, "foo.json.gz")
        persisted = Persisted(save_to)
        persisted.add("456", "b/c/d")
        persisted.save()

        reloaded_persisted = Persisted(save_to)
        self.assertTrue(reloaded_persisted.seen("456"))

    @classmethod
    def tearDownClass(cls):
        cls.test_directory.cleanup()


if __name__ == "__main__":
    unittest.main()
