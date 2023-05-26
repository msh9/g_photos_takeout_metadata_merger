import unittest
import pathlib
import exif
import tempfile
from photo_metadata_merger.exifio.content import JpgContent
from photo_metadata_merger.exifio.metadata import TakeoutMetadata
import constants
import json

class TestJpgContent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_output_directory = tempfile.TemporaryDirectory()
        content_path = constants.get_exif_fixture_path()
        with open(content_path, 'rb') as image_file:
            image = image_file.read()

        mock_metadata_dict = {
            "creationTime": {"timestamp": "1684784093"},
            "photoTakenTime": {"timestamp": "1621573200"},
            "geoData": {"latitude": 45.4215, "longitude": -75.6972},
            "geoDataExif": {"latitude": 45.4215, "longitude": -75.8972},
            "title": "test_photo",
            "description": "foo"
        }

        cls.test_file_path = pathlib.Path(cls.test_output_directory.name, "test.jpg")
        metadata = TakeoutMetadata(json.dumps(mock_metadata_dict))

        jpg_content = JpgContent(image, metadata)
        jpg_content.process_content_metadata(cls.test_file_path)

        with open(cls.test_file_path, 'rb') as fixture_image:
            cls.test_fixture = fixture_image.read()

    def test_process_content_exists(self):
        self.assertTrue(TestJpgContent.test_file_path.exists())

    def test_process_content_updates_timestamps(self):
        exif_data = exif.Image(TestJpgContent.test_fixture)

        self.assertEqual(exif_data.get('datatime_original'), '2021-05-21 00:00')
        self.assertEqual(exif_data.get('datatime_digitized'), '2023-05-22 13:34:53')

    def test_process_content_updates_location(self):
        exif_data = exif.Image(TestJpgContent.test_fixture)

        latitude_degrees_minutes_seconds = exif_data.get('gps_latitude')
        longitude_degrees_minutes_seconds = exif_data.get('gps_longitude')

        self.assertAlmostEqual(45.4215, TestJpgContent._deg_minute_second_to_decimal(*latitude_degrees_minutes_seconds))
        self.assertAlmostEqual(75.8972, TestJpgContent._deg_minute_second_to_decimal(*longitude_degrees_minutes_seconds))

        self.assertEqual(exif_data.get('gps_latitude_ref'), 'N')
        self.assertEqual(exif_data.get('gps_longitude_ref'), 'W')

    def test_process_content_updates_title(self):
        exif_data = exif_data(TestJpgContent.test_fixture)

        self.assertEqual(exif_data.get('xp_title'), 'test_photo')

    @staticmethod
    def _deg_minute_second_to_decimal(degrees, minutes, seconds) -> float:
        return (degrees +
                minutes / 60 +
                seconds / 60)

    @classmethod
    def tearDownClass(cls):
        cls.test_output_directory.cleanup()

if __name__ == "__main__":
    unittest.main()
