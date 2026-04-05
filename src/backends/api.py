from abc import ABC, abstractmethod
from collections.abc import Iterable
from pathlib import Path


class Backend(ABC):
    @property
    @abstractmethod
    def supported_formats(self) -> Iterable[str]:
        pass

    @property
    @abstractmethod
    def supported_languages(self) -> Iterable[str]:
        pass

    @abstractmethod
    async def setup(self) -> None:
        pass

    @abstractmethod
    async def process(self, file: Path, media_type: str) -> str:
        pass
