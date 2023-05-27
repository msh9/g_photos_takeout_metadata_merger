from dataclasses import dataclass
from fractions import Fraction
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

    def get_description(self) -> str:
        return self._metadata['description']

class Location:
    """Represents a physical location recorded by Google Photos"""

    def __init__(self, latitude: float, longitude: float) -> None:
        self.latitude = Coordinate(latitude)
        self.longitude = Coordinate(longitude)

    def get_latitude_as_deg_minutes_seconds(self) -> str:
        return self.latitude.as_rational_string()

    def get_longitude_as_deg_minutes_seconds(self) -> str:
        return self.longitude.as_rational_string()

    def is_latitude_north(self) -> bool:
        return self.latitude.coordinate > 0

    def is_longitude_west(self) -> bool:
        return self.longitude.coordinate < 0

class Coordinate:
    "Represents a single coordinate, eg a latitude"

    def __init__(self, coordinate: float):
        self.coordinate = coordinate

    def as_rational_string(self) -> str:
        rational_location = Coordinate._convert_to_fractional_dms(self.coordinate)
        degrees = Coordinate._stringify_rational(rational_location[0])
        minutes = Coordinate._stringify_rational(rational_location[1])
        seconds = Coordinate._stringify_rational(rational_location[2])

        return f'{degrees} {minutes} {seconds}'

    @staticmethod
    def _stringify_rational(rational: Fraction) -> str:
        limited = rational.limit_denominator(1000)
        return f'{limited.numerator}/{limited.denominator}'

    @staticmethod
    def _convert_to_fractional_dms(decimal_degrees: float) -> tuple[Fraction, Fraction, Fraction]:
        absolute_degrees = abs(decimal_degrees)
        degrees = Fraction(math.trunc(absolute_degrees))
        remainder_of_degrees = absolute_degrees - degrees

        decimal_minutes = remainder_of_degrees * _minutes_per_degree
        minutes = Fraction(math.trunc(decimal_minutes))
        remainder_of_minutes = decimal_minutes - minutes

        seconds = Fraction(remainder_of_minutes * _seconds_per_minute)
        return (degrees, minutes, seconds)

