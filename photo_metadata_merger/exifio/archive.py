import tarfile
from pathlib import PurePath

_supported_image_file_extensions = [".jpg", ".jpeg", ".dng", ".png"]
_supported_video_file_extensions = [".mkv", ".mp4"]
_json_file_suffix = '.json'

class PhotoArchive:
    """PhotoArchive provides streaming methods for reading photos and metadata in pairs from Google Takeout Archives"""

    def __init__(self, tarfile_path) -> None:
        self.tarfile_path = tarfile_path
        self.archive_iterator = None
    
    def __enter__(self):
        self.archive = tarfile.open(self.tarfile_path, 'r:gz')
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.archive.close()
        return False

    def __iter__(self):
        return self
    
    def __next__(self):
        return self._get_next_non_metadata_file()

    def _is_file_image_or_video(path):
        compressed_file_suffix = path.suffix
        return (compressed_file_suffix in _supported_image_file_extensions or
                    compressed_file_suffix in _supported_video_file_extensions)

    def _get_next_non_metadata_file(self):
        if self.archive_iterator is None:
            self.archive_iterator = iter(self.archive)

        try:
            while True:
                compressed_file = next(self.archive_iterator)
                if compressed_file.isfile():
                    name_as_path = PurePath(compressed_file.name)
                    is_image_or_video = PhotoArchive._is_file_image_or_video(name_as_path)
                    if is_image_or_video:
                        metadata_file_path = name_as_path.with_suffix(name_as_path.suffix + _json_file_suffix)
                        return (name_as_path, metadata_file_path)
        except StopIteration as ex:
            self.archive_iterator = None
            raise ex