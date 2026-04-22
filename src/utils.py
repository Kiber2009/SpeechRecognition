from collections.abc import Callable, Collection
from pathlib import Path
from typing import Union


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def stable_partition[T](
    collection: Collection[T], predicate: Callable[[T], bool]
) -> list[T]:
    return sorted(collection, key=lambda x: not predicate(x))


class DynamicUnionType[T]:
    def __init__(self):
        self.types: list[type[T]] = []

    def add(self, *types: type[T]) -> None:
        self.types += types

    def get(self) -> type[T] | None:
        if len(self.types) == 0:
            return None
        return Union[*self.types]

    def __call__[C: type[T]](self, cls: C) -> C:
        self.add(cls)
        return cls


class ValueStore[T]:
    def __init__(self, value: T | None = None) -> None:
        self.value = value

    def set(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        if self.value is None:
            raise ValueError("No value stored")
        return self.value
