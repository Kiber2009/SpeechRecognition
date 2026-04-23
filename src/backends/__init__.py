import logging
from collections.abc import Iterable

from backends.api import Backend
from backends.vosk import VoskModelConfig
from config import config, model_config_types
from utils import ValueStore, stable_partition

model_config_types.add(VoskModelConfig)

backends = ValueStore[dict[str, Backend]]()


async def setup_backends(names: set[str] | None) -> None:
    models = config.get().models.copy()

    if names is None:
        names: set[str] = set(models.keys())

    backs = {k: v.get_backend() for k, v in models.items() if k in names}

    for k, v in backs.items():
        logging.info(f"Setting up backend: {k}")
        await v.setup()

    backends.set(backs)


def select_backend(languages: Iterable[str | None] | None = None) -> Backend:
    backs = backends.get()

    res = list(backs.keys())

    if languages is not None:
        res = stable_partition(
            res,
            lambda x: all(
                map(lambda y: y in backs[x].supported_languages, languages or ())
            ),
        )

    return backs[res[0]]
