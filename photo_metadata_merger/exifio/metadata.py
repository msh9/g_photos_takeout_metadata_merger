from dataclasses import dataclass
import datetime
import json
import math

_minutes_per_degree = 60
_seconds_per_minute = 60

class TakeoutMetadata:
    """TakeoutMetadata loads google takeout metadata for photos for use elsewhere"""

    def __init__(self, metadata) -> None:
        """Creates a TakeoutMetadata object from a string, bytes, or bytearray of takeout metadata"""
        self._metadata = json.loads(metadata)

    def get_creation_time(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(int(self._metadata['creationTime']['timestamp']), datetime.timezone.utc) 

    def get_photo_taken_time(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(int(self._metadata['photoTakenTime']['timestamp']), datetime.timezone.utc)

    def get_gphotos_location(self) -> 'Location':
        geoData = self._metadata['geoData']
        return Location(geoData['latitude'], geoData['longitude'])

    def get_exif_location(self) -> 'Location':
        exif_geo_data = self._metadata['geoDataExif']
        return Location(exif_geo_data['latitude'], exif_geo_data['longitude'])

    def get_title(self) -> str:
        return self._metadata['title']

@dataclass
class Location:
    """Represents a physical location recorded by Google Photos"""

    latitude: float
    longitude: float

    def get_latitude_as_deg_minutes_seconds(self) -> tuple[int, int, float]:
        return Location._convert_to_dms(self.latitude)


    def get_longitude_as_deg_minutes_seconds(self) -> tuple[int, int, float]:
        return Location._convert_to_dms(self.longitude)

    def is_latitude_north(self) -> bool:
        return self.latitude > 0

    def is_longitude_west(self) -> bool:
        return self.longitude < 0

    @staticmethod
    def _convert_to_dms(decimal_degrees: float) -> tuple[int, int, float]:
        absolute_degrees = abs(decimal_degrees)
        degrees = math.trunc(absolute_degrees)
        remainder_of_degrees = absolute_degrees - degrees

        decimal_minutes = remainder_of_degrees * _minutes_per_degree
        minutes = math.trunc(decimal_minutes)
        remainder_of_minutes = decimal_minutes - minutes

        seconds = remainder_of_minutes * _seconds_per_minute
        return (degrees, minutes, seconds)