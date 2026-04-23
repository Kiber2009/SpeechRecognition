import asyncio
import logging
from shutil import rmtree
from sys import argv, stdin

from backends import setup_backends
from config import load_config
from env import SETTINGS
from runner import run_services
from services import Service, get_services

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG if SETTINGS.DEBUG else logging.INFO,
        format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
    )

    services: dict[str, Service] = get_services(
        args if len(args := argv[1:]) >= 1 else None
    )

    load_config(stdin.read())

    logging.info(f"Selected backends: {', '.join(SETTINGS.INCLUDE_BACKENDS)}")
    asyncio.run(setup_backends(SETTINGS.INCLUDE_BACKENDS))

    logging.info(f"Selected services: {', '.join(services)}")
    asyncio.run(run_services(services))

    rmtree(SETTINGS.TEMP_DIR)
