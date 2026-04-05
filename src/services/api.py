import asyncio
from abc import ABC, abstractmethod
from asyncio import Task


class Service(ABC):
    def prepare(self) -> None:
        pass

    @abstractmethod
    async def main(self, name: str) -> None:
        pass

    def cleanup(self) -> None:
        pass

    def get_task(self, name: str) -> Task[None]:
        return asyncio.create_task(self.main(name))
