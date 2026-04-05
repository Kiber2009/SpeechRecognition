import logging
from collections.abc import Iterable

from backends.api import Backend
from backends.vosk import VoskBackend
from utils import stable_partition

BACKENDS: dict[str, Backend] = {
    "vosk_ru": VoskBackend("vosk-model-ru-0.42", "ru"),
    "vosk_ru_small": VoskBackend("vosk-model-small-ru-0.22","ru"),
}


async def setup_backends(names: set[str] | None) -> None:
    if names is None:
        names = set(BACKENDS.keys())

    for i in set(BACKENDS.keys()):
        if i not in names:
            del BACKENDS[i]
            continue

        logging.info(f"Setting up backend: {i}")
        await BACKENDS[i].setup()


def select_backend(languages: Iterable[str] | None = None) -> Backend:
    res = list(BACKENDS.keys())

    if languages is not None:
        res = stable_partition(
            res,
            lambda x: all(
                map(lambda y: y in BACKENDS[x].supported_languages, languages)
            ),
        )

    return BACKENDS[res[0]]
