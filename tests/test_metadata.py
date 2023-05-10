import unittest
import constants
import pathlib
import datetime
from photo_metadata_merger.exifio import metadata

class TestMetadata(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        metadata_path = pathlib.Path(__file__).parent.absolute().joinpath(constants.resource_directory).joinpath(constants.image_metadata_filename)
        with open(metadata_path, 'r') as metadata:
            cls.photo_fixture = metadata.read()

    def test_get_creation_time(self):
        photo_metadata = metadata.TakeoutMetadata(TestMetadata.photo_fixture)
        correct_creation_time = datetime.datetime.fromtimestamp(1621897037, datetime.timezone.utc)
        self.assertEqual(correct_creation_time, photo_metadata.get_creation_time())

    def test_get_photo_taken_time(self):
        photo_metadata = metadata.TakeoutMetadata(TestMetadata.photo_fixture)
        pass

    def test_get_title(self):
        photo_metadata = metadata.TakeoutMetadata(TestMetadata.photo_fixture)
        pass

if __name__ == '__main__':
    unittest.main()