from abc import ABC, abstractmethod
from io import IOBase
import metadata
import pathlib

class Content(ABC):
    """Base interface for processing metadata into content files"""

    def __init__(self, content: IOBase, metadata: IOBase ) -> None:
        self._content = content
        self._metadata = metadata
        super().__init__()

    @abstractmethod
    def open(self) -> None:
        pass

    @abstractmethod
    def update(self, metadata: metadata.TakeoutMetadata) -> None:
        pass

    @abstractmethod
    def save(self, save_to_directory: pathlib.PurePath) -> None:
        pass

class JpgContent(Content):
    """Support for jpeg images with exif metadata"""

    def open(self) -> None:
        pass