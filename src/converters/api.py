from abc import ABC, abstractmethod
from pathlib import Path


class Converter(ABC):
    @abstractmethod
    async def convert(
        self,
        source: Path,
        source_type: str,
        result: Path,
        result_type: str,
    ) -> None:
        pass
