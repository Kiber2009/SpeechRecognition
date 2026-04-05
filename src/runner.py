import asyncio
import logging

from services import Service

logger = logging.getLogger(__name__)


async def _run_service(name: str, service: Service, stop_event: asyncio.Event) -> None:
    restart_delay = 1

    while not stop_event.is_set():
        logger.info("Service %s: preparing", name)

        try:
            service.prepare()
        except Exception as e:
            logger.exception(f"Service %s: prepare() failed ({e!r})", name)
            await asyncio.sleep(restart_delay)
            continue

        logger.info("Service %s: starting", name)

        try:
            task = service.get_task(name)
            await task

            logger.warning(
                "Service %s: finished unexpectedly, restarting", name
            )
        except asyncio.CancelledError:
            logger.info("Service %s: cancelled", name)
            raise
        except Exception as e:
            logger.exception(f"Service %s: crashed, restarting ({e!r})", name)
        finally:
            try:
                logger.info("Service %s: cleanup", name)
                service.cleanup()
            except Exception as e:
                logger.exception(f"Service %s: cleanup() failed ({e!r})", name)

        if not stop_event.is_set():
            logger.info(
                "Service %s: restarting in %s seconds", name, restart_delay
            )
            try:
                await asyncio.sleep(restart_delay)
            except asyncio.CancelledError:
                break


async def run_services(services: dict[str, Service]) -> None:
    stop_event = asyncio.Event()

    tasks = [
        asyncio.create_task(_run_service(name, service, stop_event), name=f"svc:{name}")
        for name, service in services.items()
    ]

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        logger.info("Shutdown requested")
    finally:
        stop_event.set()

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

        logger.info("All services stopped")