from typing import Type
import unittest
import pathlib
import pyexiv2
import tempfile
from photo_metadata_merger.exifio.content import GenericXMPExifContent, GenericXMPContent, XMPSidecar
from photo_metadata_merger.exifio.metadata import TakeoutMetadata
import constants
import json

mock_metadata_dict = {
    "creationTime": {"timestamp": "1684784093"},
    "photoTakenTime": {"timestamp": "1621573200"},
    "geoData": {"latitude": 45.4215, "longitude": -75.6972},
    "geoDataExif": {"latitude": 45.4215, "longitude": -75.8972},
    "title": "test",
    "description": "foo"
}

class TestGenericXMPExifContent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_output_directory = tempfile.TemporaryDirectory()
        content_path = constants.get_exif_fixture_path()
        with open(content_path, 'rb') as image_file:
            image = image_file.read()

        cls.test_file_path = pathlib.Path(cls.test_output_directory.name, "test.jpg")
        metadata = TakeoutMetadata(json.dumps(mock_metadata_dict))

        jpg_content = GenericXMPExifContent(image, metadata)
        jpg_content.process_content_metadata(cls.test_file_path)

        with open(cls.test_file_path, 'rb') as fixture_image:
            cls.test_fixture = fixture_image.read()

    def test_process_content_exists(self):
        self.assertTrue(TestGenericXMPExifContent.test_file_path.exists())

    def test_process_content_updates_timestamps(self):
        with pyexiv2.ImageData(TestGenericXMPExifContent.test_fixture) as image_data:
            exif = image_data.read_exif()
            self.assertEqual(exif['Exif.Photo.DateTimeOriginal'], '2021-05-21 05:00:00+00:00')
            self.assertEqual(exif['Exif.Photo.DateTimeDigitized'], '2023-05-22 19:34:53+00:00')

    def test_process_content_updates_location(self):
        with pyexiv2.ImageData(TestGenericXMPExifContent.test_fixture) as image_data:
            exif = image_data.read_exif()
            self.assertEqual(exif['Exif.GPSInfo.GPSLatitudeRef'], 'N')
            self.assertEqual(exif['Exif.GPSInfo.GPSLongitudeRef'], 'W')

            self.assertEqual(exif['Exif.GPSInfo.GPSLatitude'], '45/1 25/1 87/5')
            self.assertEqual(exif['Exif.GPSInfo.GPSLongitude'], '75/1 41/1 1248/25')

    def test_process_content_updates_title(self):
        with pyexiv2.ImageData(TestGenericXMPExifContent.test_fixture) as image_data:
            exif = image_data.read_exif()
            self.assertEqual(exif['Exif.Image.XPTitle'], 'test')

    @classmethod
    def tearDownClass(cls):
        cls.test_output_directory.cleanup()


def createXMPTestClass(fixture_file: pathlib.PurePath, test_fixture_output_name: str) -> Type[unittest.TestCase]:
    class TestGenericXMPContent(unittest.TestCase):

        @classmethod
        def setUpClass(cls):
            cls.test_output_directory = tempfile.TemporaryDirectory()
            with open(fixture_file, 'rb') as media_file:
                video = media_file.read()

            cls.test_file_path = pathlib.Path(cls.test_output_directory.name, test_fixture_output_name)
            metadata = TakeoutMetadata(json.dumps(mock_metadata_dict))

            mp4_content = GenericXMPContent(video, metadata)
            mp4_content.process_content_metadata(cls.test_file_path)

            with open(cls.test_file_path, 'rb') as media_fixture:
                cls.test_fixture = media_fixture.read()

        def test_process_content_exists(self):
            self.assertTrue(TestGenericXMPContent.test_file_path.exists())

        def test_process_content_updates_xmp_dates(self):
            with pyexiv2.ImageData(TestGenericXMPContent.test_fixture) as content:
                xmp = content.read_xmp()
                self.assertEqual(xmp['Xmp.xmp.CreateDate'], '2021-05-21 05:00:00+00:00')
                self.assertEqual(xmp['Xmp.exif.DateTimeOriginal'], '2021-05-21 05:00:00+00:00')
                self.assertEqual(xmp['Xmp.exif.DateTimeDigitized'], '2023-05-22 19:34:53+00:00')

        def test_process_content_updates_xmp_title_description(self):
            with pyexiv2.ImageData(TestGenericXMPContent.test_fixture) as content:
                xmp = content.read_xmp()
                self.assertEqual(xmp['Xmp.dc.description'], {'lang="x-default"': 'foo'})
                self.assertEqual(xmp['Xmp.exif.ImageDescription'], 'foo')
            
        def test_process_content_updates_xmp_exif_gps(self):
            with pyexiv2.ImageData(TestGenericXMPContent.test_fixture) as content:
                xmp = content.read_xmp()
                self.assertEqual(xmp['Xmp.exif.GPSLatitude'], '45/1 25/1 87/5')
                self.assertEqual(xmp['Xmp.exif.GPSLongitude'], '75/1 41/1 1248/25')

        @classmethod
        def tearDownClass(cls):
            cls.test_output_directory.cleanup()

    return TestGenericXMPContent

pngXMPTest = createXMPTestClass(constants.get_xmp_fixture_path(), 'test.png')
globals()['PngXMPTest'] = pngXMPTest

class TestXMPSidecar(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_output_directory = tempfile.TemporaryDirectory()
        content_path = constants.get_xmp_fixture_path()
        with open(content_path, 'rb') as media_file:
            media = media_file.read()

        cls.test_file_path = pathlib.Path(cls.test_output_directory.name, "test.png")
        metadata = TakeoutMetadata(json.dumps(mock_metadata_dict))

        content = XMPSidecar(media, metadata)
        content.process_content_metadata(cls.test_file_path)

        # TODO: this needs to pull up the sidecar instead of the media file
        with open(cls.test_file_path, 'rb') as media:
            cls.media_test_fixture = media.read()
        
        metadata = cls.test_file_path.suffix('.xmp')

    def test_process_content_writes_sidecar(self):
        pass

    def test_process_content_writes_media_identically(self):
        pass


if __name__ == "__main__":
    unittest.main()
