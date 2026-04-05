from pathlib import Path

from converters.api import Converter
from converters.ffmpeg_ import FFmpegConverter
from env import SETTINGS
from utils import ensure_dir

CONVERTERS: dict[str, Converter] = {"ffmpeg": FFmpegConverter()}

CONVERTED_PATH = ensure_dir(SETTINGS.TEMP_DIR / "converted")


async def convert(
    source: Path,
    source_type: str,
    *result_type: str,
) -> tuple[Path, str]:
    if source_type in result_type:
        return source, source_type

    conv = CONVERTERS[SETTINGS.CONVERTER]

    path = (CONVERTED_PATH / source.name).absolute()

    await conv.convert(source, source_type, path, result_type[0])

    return path, result_type[0]
