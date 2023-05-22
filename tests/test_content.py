import unittest
import pathlib
import exif
import os
import tempfile
from content import JpgContent
from metadata import TakeoutMetadata, Location
import constants

class TestJpgContent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a temporary directory for saving images
        cls.temp_dir = tempfile.TemporaryDirectory()

    @classmethod
    def tearDownClass(cls):
        # Clean up the temporary directory after all tests are done
        cls.temp_dir.cleanup()

    def setUp(self):
        # Prepare a sample JpgContent instance for use in tests.
        # This uses an actual image file and mock metadata.
        content_path = constants.get_image_path()
        with open(content_path, 'rb') as f:
            content = f.read()

        mock_metadata_dict = {
            "creationTime": {"timestamp": "1621573200"},
            "photoTakenTime": {"timestamp": "1621573200"},
            "geoData": {"latitude": 45.4215, "longitude": -75.6972},
            "geoDataExif": {"latitude": 45.4215, "longitude": -75.6972},
            "title": "test_photo"
        }
        metadata = TakeoutMetadata(mock_metadata_dict)
        self.jpg_content = JpgContent(content, metadata)

    def test_update_content_metadata_datetime_original(self):
        # Update metadata
        updated_image = self.jpg_content._update_content_metadata()

        # Check the datetime_original field
        self.assertEqual(updated_image.datetime_original, "2021-05-21 00:00")

    def test_save_content(self):
        # Define the path to save the content to
        save_to_path = pathlib.PurePath(self.temp_dir.name, "test.jpg")

        # Update metadata and save the content
        updated_image = self.jpg_content._update_content_metadata()
        self.jpg_content._save_content(updated_image, save_to_path)

        # Check that the file was saved successfully
        self.assertTrue(os.path.isfile(save_to_path))

if __name__ == "__main__":
    unittest.main()
