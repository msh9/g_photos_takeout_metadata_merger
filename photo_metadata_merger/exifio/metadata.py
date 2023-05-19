import datetime
import json

class TakeoutMetadata:
    """TakeoutMetadata loads google takeout metadata for photos for use elsewhere"""

    def __init__(self, metadata) -> None:
        """Creates a TakeoutMetadata object from a string, bytes, or bytearray of takeout metadata"""
        self._metadata = json.loads(metadata)

    def get_creation_time(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(int(self._metadata['creationTime']['timestamp']), datetime.timezone.utc) 

    def get_photo_taken_time(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(int(self._metadata['photoTakenTime']['timestamp']), datetime.timezone.utc)

    def get_gphotos_location(self):
        geoData = self._metadata['geoData']
        return Location(geoData['latitude'], geoData['longitude'])

    def get_exif_location(self):
        exif_geo_data = self._metadata['geoDataExif']
        return Location(exif_geo_data['latitude'], exif_geo_data['longitude'])

    def get_title(self) -> str:
        return self._metadata['title']

class Location:
    """Represents a physical location recorded by Google Photos"""

    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude