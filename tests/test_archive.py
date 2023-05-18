import unittest
import tarfile
import tempfile
import pathlib
import constants
from photo_metadata_merger.exifio import archive

_resource_directory = 'resources'


class TestArchive(unittest.TestCase):

    @staticmethod
    def _create_test_archive_from_directory(archive: tarfile.TarFile, directory_name: str) -> None:
            cls_path = pathlib.Path(__file__).parent.absolute()
            for resource_to_be_tarred in cls_path.joinpath(directory_name).iterdir():
                TestArchive._add_file_with_base_name_only_to_archive(archive, resource_to_be_tarred)

    @staticmethod
    def _add_file_with_base_name_only_to_archive(tar: tarfile.TarFile, to_be_tarred: str) -> None:
        resource_name_only = pathlib.PurePath(to_be_tarred).name
        tar.add(to_be_tarred, arcname=resource_name_only, recursive=False)

    @classmethod
    def setUpClass(cls):
        cls._archive_directory = tempfile.TemporaryDirectory()
        cls.first_archive_path = pathlib.Path(TestArchive._archive_directory.name, 'test1.tgz')
        
        with tarfile.open(cls.first_archive_path, mode= "w:gz") as archive:
            TestArchive._create_test_archive_from_directory(archive, constants.tarone_resource_directory)

        cls.second_archive_path = pathlib.Path(TestArchive._archive_directory.name, 'test2.tgz')

        with tarfile.open(cls.second_archive_path, mode= "w:gz") as archive:
            TestArchive._create_test_archive_from_directory(archive, constants.tartwo_resource_directory)
    
    def test_photo_archive_context(self):
        with archive.Archive(TestArchive.first_archive_path) as pa:
            self.assertIsInstance(pa, archive.Archive)

    def test_photo_archive_gets_next_image(self):
        with archive.Archive(TestArchive.first_archive_path) as pa:
            non_metadata_path, metadata_path = next(pa)
            self.assertIsNotNone(non_metadata_path)
            self.assertIsNotNone(metadata_path)
            self.assertFalse(non_metadata_path.name.endswith('.json'))
            self.assertTrue(metadata_path.name.endswith('.json'))

    def test_photo_archive_returns_correct_metadata_per_image(self):
        with archive.Archive(TestArchive.first_archive_path) as pa:
            non_metadata_archive_path, metadata_archive_path = next(pa)
            non_metadata_path = pathlib.PurePath(non_metadata_archive_path)
            self.assertEqual(pathlib.PurePath(metadata_archive_path), non_metadata_path.with_suffix(non_metadata_path.suffix + '.json')) 

    def test_photo_archive_returns_only_metadata_in_second_tuple_value(self):
        with archive.Archive(TestArchive.first_archive_path, TestArchive.second_archive_path) as pa:
            for _, metadata_archive_location in pa:
                metadata_path = pathlib.PurePath(metadata_archive_location)
                self.assertFalse(metadata_path.suffix != '.json')

    def test_photo_archive_only_returns_metadata_for_extant_images(self):
        with archive.Archive(TestArchive.first_archive_path, TestArchive.second_archive_path) as pa:
            for _, metadata_archive_location in pa:
                metadata_path = pathlib.PurePath(metadata_archive_location)
                self.assertFalse(metadata_path.name == 'other-img.jpg.json')

    def test_photo_archive_fails_on_missing_content_metadata(self):
        with archive.Archive(TestArchive.first_archive_path) as pa:
            with self.assertRaises(archive.MetadataNotFound):
                for _, _ in pa:
                    continue

    @classmethod
    def tearDownClass(cls):
        cls._archive_directory.cleanup()

if __name__ == '__main__':
    unittest.main()