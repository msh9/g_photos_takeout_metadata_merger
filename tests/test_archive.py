import io
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
    
    def test_archive_context(self):
        with archive.Archive(TestArchive.first_archive_path) as pa:
            self.assertIsInstance(pa, archive.Archive)

    def test_archive_gets_next_image(self):
        with archive.Archive(TestArchive.first_archive_path) as pa:
            archive_pair = next(pa)
            self.assertIsNotNone(archive_pair.content_file)
            self.assertIsNotNone(archive_pair.metadata_file)

    def test_archive_returns_correct_metadata_per_image(self):
        with archive.Archive(TestArchive.first_archive_path) as pa:
            archive_pair = next(pa)
            content_path = pathlib.PurePath(archive_pair.content_file.name)
            metadata_path = pathlib.PurePath(archive_pair.metadata_file.name)
            self.assertEqual(metadata_path, content_path.with_suffix(content_path.suffix + '.json')) 

    def test_archive_only_returns_metadata_for_extant_images(self):
        with archive.Archive(TestArchive.first_archive_path, TestArchive.second_archive_path) as pa:
            for archive_pair in pa:
                metadata_path = pathlib.PurePath(archive_pair.metadata_file.name)
                self.assertFalse(metadata_path.name == 'other-img.jpg.json')

    def test_archive_fails_on_missing_content_metadata(self):
        with archive.Archive(TestArchive.first_archive_path) as pa:
            with self.assertRaises(archive.MetadataNotFound):
                for _ in pa:
                    continue

    def test_archive_extracts_files_from_archive(self):
        with archive.Archive(TestArchive.first_archive_path, TestArchive.second_archive_path) as pa:
            archive_pair = next(pa)
            content, metadata = pa.extract_files(archive_pair)
            self.assertIsNotNone(content)
            self.assertIsNotNone(metadata)
            self.assertIsInstance(content, io.IOBase)
            self.assertIsInstance(metadata, io.IOBase)

    @classmethod
    def tearDownClass(cls):
        cls._archive_directory.cleanup()

if __name__ == '__main__':
    unittest.main()