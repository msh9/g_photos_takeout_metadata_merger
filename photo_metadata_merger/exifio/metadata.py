import datetime
import json

class TakeoutMetadata:
    """TakeoutMetadata loads google takeout metadata for photos for use elsewhere"""

    def __init__(self, metadata) -> None:
        """Creates a TakeoutMetadata object from a string, bytes, or bytearray of takeout metadata"""
        self._metadata = json.loads(metadata)

    def get_creation_time(self) -> datetime.datetime:
        if ('creationTime' in self._metadata 
            and 'timestamp' in self._metadata['creationTime']):
            return datetime.datetime.fromtimestamp(int(self._metadata['creationTime']['timestamp']), datetime.timezone.utc) 
        else:
            raise KeyError

    def getPhotoTakenTime(self) -> datetime.datetime:
        pass

    def get_title(self) -> str:
        pass