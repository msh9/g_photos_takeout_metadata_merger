from abc import ABC, abstractmethod
from typing import IO
from photo_metadata_merger.exifio.metadata import TakeoutMetadata
import pathlib
import pyexiv2

_xmp_sidecar_starter_content = (b'<?xpacket begin="\xef\xbb\xbf" id="W5M0MpCehiHzreSzNTczkc9d"?>'
                                b'<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="XMP Core 4.4.0-Exiv2">'
                                b'<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
                                b'<rdf:Description rdf:about="">'
                                b'</rdf:Description>'
                                b'</rdf:RDF>'
                                b'</x:xmpmeta>'
                                b'<?xpacket end="w"?>')

_xmp_sidecar_extension = '.xmp'

class Content(ABC):
    """Base interface for processing metadata into content files"""

    def __init__(self, content: IO[bytes], metadata: TakeoutMetadata) -> None:
        self._content = content
        self._metadata = metadata
        super().__init__()

    def process_content_metadata(self, save_to_path: pathlib.PurePath) -> None:
        with pyexiv2.ImageData(self._content) as content:
            self._update_content_data(content)
            Content._save_content(content.get_bytes(), save_to_path)

    def _set_xmp_title_date_description(self, content: pyexiv2.ImageData) -> None:
        content.modify_xmp({
            'Xmp.xmp.CreateDate': self._metadata.get_photo_taken_time(),
            'Xmp.dc.title': {'lang="x-defualt"': self._metadata.get_title()},
            'Xmp.dc.description': {'lang="x-default"': self._metadata.get_description()}
        })

    @staticmethod
    def _save_content(content: bytes, save_to_path: pathlib.PurePath) -> None:
        with open(save_to_path, 'wb') as image_file:
            image_file.write(content)

    @abstractmethod
    def _update_content_data(content: pyexiv2.ImageData) -> None:
        pass

class GenericXMPContent(Content):
    """Relies on exiv2 library to supports files needing XMP formatted metadata only"""

    def _update_content_data(self, content: pyexiv2.ImageData) -> None:
        self._set_xmp_title_date_description(content)
        self._set_exif_in_xmp(content)

    def _set_exif_in_xmp(self, content: pyexiv2.ImageData) -> None:
        photo_location = self._metadata.get_gphotos_location()
        content.modify_xmp({
            'Xmp.exif.DateTimeOriginal': self._metadata.get_photo_taken_time(),
            'Xmp.exif.DateTimeDigitized': self._metadata.get_creation_time(),
            'Xmp.exif.GPSLatitude': photo_location.get_latitude_as_deg_minutes_seconds(),
            'Xmp.exif.GPSLongitude': photo_location.get_longitude_as_deg_minutes_seconds(),
            'Xmp.exif.ImageDescription': self._metadata.get_description()
        })

class GenericXMPExifContent(Content):
    """Extends generic XMP with support for writing EXIF style metadata as well"""

    def _update_content_data(self, content: pyexiv2.ImageData) -> None:
        self._update_exif_metadata(content)
        self._set_xmp_title_date_description(content)

    def _update_exif_metadata(self, image_content: pyexiv2.ImageData) -> None:
        photo_location = self._metadata.get_gphotos_location()
        image_content.modify_exif({
            'Exif.Photo.DateTimeOriginal': self._metadata.get_photo_taken_time(),
            'Exif.Photo.OffsetTimeOriginal': '0',
            'Exif.Photo.DateTimeDigitized': self._metadata.get_creation_time().isoformat(),
            'Exif.Photo.OffsetTimeDigitized': '0',
            'Exif.Image.XPTitle': self._metadata.get_title(),
            'Exif.GPSInfo.GPSLatitude': photo_location.get_latitude_as_deg_minutes_seconds(),
            'Exif.GPSInfo.GPSLatitudeRef': 'N' if photo_location.is_latitude_north() else 'S',
            'Exif.GPSInfo.GPSLongitude': photo_location.get_longitude_as_deg_minutes_seconds(),
            'Exif.GPSInfo.GPSLongitudeRef': 'W' if photo_location.is_longitude_west() else 'E',
            'Exif.Image.ImageDescription': self._metadata.get_description()
        })

class XMPSidecar(GenericXMPContent):
    """Supports writing XMP formatted information to a sidecar file instead of the main content file"""

    def __init__(self, content: IO[bytes], metadata: TakeoutMetadata):
        super().__init__(_xmp_sidecar_starter_content, metadata)
        self._media_content = content

    def process_content_metadata(self, save_to_path: pathlib.PurePath) -> None:
        content_path = save_to_path
        metadata_path = save_to_path.suffix(_xmp_sidecar_extension)
        sidecar_content = XMPSidecar._create_xmp_starter()

        self._update_content_data(sidecar_content)
        self._save_content(self._media_content, content_path)
        self._save_content(sidecar_content.get_bytes(), metadata_path)

    @staticmethod
    def _create_xmp_starter() -> pyexiv2.ImageData:
        return pyexiv2.ImageData(_xmp_sidecar_starter_content)

