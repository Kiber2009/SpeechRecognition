import logging
from pathlib import Path

from ffmpeg.asyncio import FFmpeg

from converters.api import Converter

logger = logging.getLogger(__name__)


class FFmpegConverter(Converter):
    async def convert(
        self,
        source: Path,
        source_type: str,
        result: Path,
        result_type: str,
    ) -> None:
        conv = (
            FFmpeg()
            .option("y")
            .input(source, f=source_type)
            .output(result, f=result_type)
        )

        logger.debug(conv.arguments)
        await conv.execute()
