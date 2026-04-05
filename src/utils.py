from collections.abc import Callable, Collection
from pathlib import Path


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path

def stable_partition[T](collection: Collection[T], predicate: Callable[[T], bool]) -> list[T]:
    return sorted(collection, key=lambda x: not predicate(x))