import tarfile
from pathlib import PurePath

_supported_image_file_extensions = [".jpg", ".jpeg", ".dng", ".png"]
_supported_video_file_extensions = [".mkv", ".mp4"]
_json_file_suffix = '.json'

class MetadataNotFound(Exception):

    def __init__(self, content_name: str):
        self.content_name = content_name

class Archive:
    """PhotoArchive provides streaming methods for reading photos and metadata in pairs from Google Takeout Archives"""

    def __init__(self, *tarfile_paths):
        self._tarfile_paths = tarfile_paths
        self._archive_iterators = []
        self._archives = []
    
    def __enter__(self):
        for path in self._tarfile_paths:
            archive = tarfile.open(path, 'r:gz')
            self._archives.append(archive)
            self._archive_iterators.append(iter(archive))
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        for archive in self._archives:
            archive.close()
        return False

    def __iter__(self):
        return self
    
    def __next__(self):
        return self._get_next_non_metadata_file()

    @staticmethod
    def _is_file_image_or_video(path: PurePath) -> bool:
        compressed_file_suffix = path.suffix
        return (compressed_file_suffix in _supported_image_file_extensions or
                    compressed_file_suffix in _supported_video_file_extensions)

    def _get_metadata_file_path(self, name: PurePath) -> PurePath:
        """
        Builds the metadata filename based on Google Takeout naming conventions and then checks for the metadata
        file's presence in any one of the archives being processed. 
        """
        metadata_file_path = name.with_suffix(name.suffix + _json_file_suffix)
        # the following forces the path to a posix style path. This is done because
        # 1) getmember expects an object that supports rsplit (a string in our case)
        # 2) The tarfile module object expects posix styles paths. Despite using a PurePath
        # elsewhere in this module, `name` seems to end up as a PureWindowsPath when this is
        # executed on windows. This causes getmember to fail with a KeyError when it should
        # otherwise succced.
        metadata_file_path_posix = metadata_file_path.as_posix()
        for archive in self._archives:
            try:
                archive.getmember(metadata_file_path_posix)
            except KeyError:
                continue
            else:
                return metadata_file_path
        raise MetadataNotFound(str(name))

    def _get_next_non_metadata_file(self):
        for archive_iterators in self._archive_iterators:
            try:
                while True:
                    compressed_file = next(archive_iterators)
                    if compressed_file.isfile():
                        name_as_path = PurePath(compressed_file.name)
                        is_image_or_video = Archive._is_file_image_or_video(name_as_path)
                        if is_image_or_video:
                            return (name_as_path, self._get_metadata_file_path(name_as_path))
            except StopIteration as ex:
                continue
        raise StopIteration

class ArchivePair:
    """Transfer object for pairs of names identifying data and metadata objects discovered in a takeout archive"""

    def __init__(self, data_name, metadata_name):
        self.data_name = data_name
        self.metadata_name = metadata_name