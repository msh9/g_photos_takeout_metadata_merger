import tarfile
from pathlib import PurePath
from contextlib import contextmanager

_supported_image_file_extensions = [".jpg", ".jpeg", ".dng", ".png"]
_supported_video_file_extensions = [".mkv", ".mp4"]
_json_file_suffix = '.json'

class PhotoArchive:
    """PhotoArchive provides streaming methods for reading photos and metadata in pairs from Google Takeout Archives"""

    def __init__(self, tarfile) -> None:
        self.archive = tarfile
        self.found_images = dict()
        self.found_metadata = dict()
    
    @contextmanager
    def open(path):
        """Opens the given tar archive and returns a generator of image, metadata tuples"""

        with tarfile.open(path, "r:gz") as archive:
            pa = PhotoArchive(archive)
            yield pa
    
    def __iter__(self):
        return self
    
    def __next__(self):
        return next(self._get_next_non_metadata_file())

    def _is_file_image_or_video(path):
        compressed_file_suffix = path.suffix
        return (compressed_file_suffix in _supported_image_file_extensions or
                    compressed_file_suffix in _supported_video_file_extensions)

    def _get_next_non_metadata_file(self):
        for compressed_file in self.archive:
            if compressed_file.isfile():
                name_as_path = PurePath(compressed_file.name)
                is_image_or_video = PhotoArchive._is_file_image_or_video(name_as_path)
                if is_image_or_video:
                    metadata_file_path = name_as_path.with_suffix(_json_file_suffix)
                    yield (name_as_path, metadata_file_path)