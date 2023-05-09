import unittest
import tarfile
import tempfile
import pathlib
from photo_metadata_merger.exifio import archive

_example_image_root = './resources/example-img'
_example_video_root = './resources/example-video'
_other_example_image_root = './resources/other-img'
_resource_directory = 'resources'

class TestPhotoArchive(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls._archive_directory = tempfile.TemporaryDirectory()
        cls.archive_path = pathlib.Path(TestPhotoArchive._archive_directory.name, 'test.tgz')
        cls.archive = tarfile.open(cls.archive_path, mode= "w:gz")
        cls_path = pathlib.Path(__file__).parent.absolute()
        for resource_to_be_tarred in cls_path.joinpath(_resource_directory).iterdir():
            cls.archive.add(resource_to_be_tarred)
    
    def test_photo_archive_context(self):
        with archive.PhotoArchive.open(TestPhotoArchive.archive_path) as pa:
            self.assertIsInstance(pa, archive.PhotoArchive)

    def test_photo_archive_gets_next_image(self):
        with archive.PhotoArchive.open(TestPhotoArchive.archive_path) as pa:
            non_metadata_path, metadata_path = next(pa)
            self.assertIsNotNone(non_metadata_path)
            self.assertIsNotNone(metadata_path)
            self.assertFalse(non_metadata_path.endswith('.json'))
            self.assertTrue(metadata_path.endswith('.json'))

    def test_photo_archive_returns_correct_metadata_per_image(self):
        with archive.PhotoArchive.open(TestPhotoArchive.archive_path) as pa:
            non_metadata_archive_path, metadata_archive_path = next(pa)
            non_metadata_path = pathlib.PurePath(non_metadata_archive_path)
            self.assertEqual(pathlib.PurePath(metadata_archive_path), non_metadata_path.with_suffix(non_metadata_path.suffix + '.json')) 

    def test_photo_archive_returns_only_metadata_in_second_tuple_value(self):
        with archive.PhotoArchive.open(TestPhotoArchive.archive_path) as pa:
            for _, metadata_archive_location in pa:
                metadata_path = pathlib.PurePath(metadata_archive_location)
                self.assertFalse(metadata_path.suffix != '.json')

    def test_photo_archive_only_returns_metadata_for_extant_images(self):
        with archive.PhotoArchive.open(TestPhotoArchive.archive_path) as pa:
            for _, metadata_archive_location in pa:
                metadata_path = pathlib.PurePath(metadata_archive_location)
                self.failIf(metadata_path.name == 'other-img.jpg.json')

    @classmethod
    def tearDownClass(cls):
        cls.archive.close()
        cls._archive_directory.cleanup()


if __name__ == '__main__':
    unittest.main()