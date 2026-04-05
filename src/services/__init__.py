from collections.abc import Iterable

from .api import Service
from .telegram.main import TelegramService

SERVICES: dict[str, Service] = {"telegram": TelegramService()}


def get_services(names: Iterable[str] | None) -> dict[str, Service]:
    if names is None:
        return SERVICES
    result = {}
    for i in names:
        result[i] = SERVICES[i]
    return result
