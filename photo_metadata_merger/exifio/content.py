from abc import ABC, abstractmethod
from io import IOBase
from photo_metadata_merger.exifio.metadata import TakeoutMetadata
import pathlib
import exif

class Content(ABC):
    """Base interface for processing metadata into content files"""

    def __init__(self, content: IOBase, metadata: TakeoutMetadata) -> None:
        self._content = content
        self._metadata = metadata
        super().__init__()

    @abstractmethod
    def process_content_metadata(self, save_to_path: pathlib.PurePath) -> None:
        pass

class JpgContent(Content):
    """Support for jpeg images with exif metadata"""

    def process_content_metadata(self, save_to_path: pathlib.PurePath) -> None:
        updated_content = self._update_content_metadata()
        JpgContent._save_content(updated_content, save_to_path)

    def _update_content_metadata(self) -> exif.Image:
        image = exif.Image(self._content)

        image.datatime_original = self._metadata.get_photo_taken_time().isoformat(' ', 'minutes')
        image.datetime_digitized = self._metadata.get_creation_time().isoformat(' ', 'minutes')
        
        photo_location = self._metadata.get_gphotos_location()
        image.gps_latitude = photo_location.get_latitude_as_deg_minutes_seconds()
        image.gps_latitude_ref = 'N' if photo_location.is_latitude_north() else 'S'
        image.gps_longitude = photo_location.get_longitude_as_deg_minutes_seconds()
        image.gps_longitude_ref = 'W' if photo_location.is_longitude_west() else 'E'

        image.xp_title = self._metadata.get_title()

        return image

    @staticmethod
    def _save_content(image: exif.Image, save_to_path: pathlib.PurePath) -> None:
        with open(save_to_path, 'wb') as image_file:
            image_file.write(image.get_file())