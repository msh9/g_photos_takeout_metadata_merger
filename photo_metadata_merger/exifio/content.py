from abc import ABC, abstractmethod
from typing import IO
from photo_metadata_merger.exifio.metadata import TakeoutMetadata
import pathlib
import pyexiv2

class Content(ABC):
    """Base interface for processing metadata into content files"""

    def __init__(self, content: IO[bytes], metadata: TakeoutMetadata) -> None:
        self._content = content
        self._metadata = metadata
        super().__init__()

    @abstractmethod
    def process_content_metadata(self, save_to_path: pathlib.PurePath) -> None:
        pass

class JpgContent(Content):
    """Support for jpeg images with exif metadata"""

    def process_content_metadata(self, save_to_path: pathlib.PurePath) -> None:
        updated_content = self._update_metadata()
        JpgContent._save_content(updated_content, save_to_path)

    def _update_metadata(self) -> bytes:
        with pyexiv2.ImageData(self._content) as image_content:
            self._update_exif_metadata(image_content)
            self._update_xmp_metadata(image_content)
            return image_content.get_bytes()

    def _update_exif_metadata(self, image_content: pyexiv2.ImageData) -> None:
        photo_location = self._metadata.get_gphotos_location()
        image_content.modify_exif({
            'Exif.Photo.DateTimeOriginal': self._metadata.get_photo_taken_time().isoformat(' ', 'minutes'),
            'Exif.Photo.OffsetTimeOriginal': '0',
            'Exif.Photo.DateTimeDigitized': self._metadata.get_creation_time().isoformat(' ', 'minutes'),
            'Exif.Photo.OffsetTimeDigitized': '0',
            'Exif.Image.XPTitle': self._metadata.get_title(),
            'Exif.GPSInfo.GPSLatitude': photo_location.get_latitude_as_deg_minutes_seconds(),
            'Exif.GPSInfo.GPSLatitudeRef': 'N' if photo_location.is_latitude_north() else 'S',
            'Exif.GPSInfo.GPSLongitude': photo_location.get_latitude_as_deg_minutes_seconds(),
            'Exif.GPSInfo.GPSLongitudeRef': 'W' if photo_location.is_longitude_west() else 'E',
            'Exif.Image.ImageDescription': self._metadata.get_description()
        })

    def _update_xmp_metadata(self, image_content: pyexiv2.ImageData) -> None:
        image_content.modify_xmp({
            'Xmp.xmp.CreateDate': self._metadata.get_photo_taken_time(),
            'Xmp.dc.title': {'lang="x-defualt"': self._metadata.get_title()},
            'Xmp.dc.description': {'lang="x-default"': self._metadata.get_description()}
        })

    @staticmethod
    def _save_content(image: bytes, save_to_path: pathlib.PurePath) -> None:
        with open(save_to_path, 'wb') as image_file:
            image_file.write(image)