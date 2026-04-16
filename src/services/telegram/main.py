import logging
from pathlib import Path
from tempfile import TemporaryFile

import filetype
from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import CommandStart
from aiogram.types import Audio, Message, Video, VideoNote, Voice

from backends import select_backend
from converters import convert
from env import SETTINGS
from services.api import Service
from utils import ensure_dir

bot = Bot(
    token=SETTINGS.TELEGRAM_BOT_TOKEN,
    session=AiohttpSession(proxy=SETTINGS.TELEGRAM_PROXY),
)

dp = Dispatcher()

MAX_FILE_SIZE = 20 * 1024 * 1024
DOWNLOAD_DIR = ensure_dir(SETTINGS.download_dir / "telegram")


async def process(
    data: Voice | VideoNote | Video | Audio | None,
    message: Message,
    extension: str | None = None,
) -> None:
    if data is None:
        return

    answer: Message = await message.reply("Распознаю речь\nПожалуйста подождите")

    if (data.file_size or 0) > MAX_FILE_SIZE:
        await answer.edit_text("Сообщение слишком большое")
        return

    if bot_file := (await bot.get_file(data.file_id)).file_path is None:
        await answer.edit_text("Не удалось загрузить сообщение")
        return

    with TemporaryFile("w+b", dir=DOWNLOAD_DIR, delete_on_close=False) as tmp:
        await bot.download_file(bot_file, destination=tmp)
        tmp.seek(0)
        if extension is None:
            if tmp := filetype.guess(tmp.read(261)) is None:
                await answer.edit_text("Не удалось определить формат сообщения")
                return
            extension: str = tmp.extension

        logging.debug(tmp.name)

        back = select_backend(
            languages=(
                (
                    from_user.language_code
                    if (from_user := message.from_user) is not None
                    else None
                ),
            )
        )
        res_path, res_type = await convert(
            Path(tmp.name),
            extension,
            *back.supported_formats,
        )

    res = await back.process(res_path, res_type)
    await answer.edit_text(res)

    res_path.unlink(missing_ok=True)


@dp.message(CommandStart())
async def start_command(message: Message) -> None:
    await message.reply("Отправьте боту голосовое сообщение, кружочек, аудио или видео")


@dp.message(F.voice)
async def voice_message(message: Message) -> None:
    await process(message.voice, message, "ogg")


@dp.message(F.video_note)
async def video_note_message(message: Message) -> None:
    await process(message.video_note, message, "mp4")


@dp.message(F.video)
async def video_message(message: Message) -> None:
    await process(message.video, message)


@dp.message(F.audio)
async def audio_message(message: Message) -> None:
    await process(message.audio, message)


class TelegramService(Service):
    async def main(self, name: str) -> None:
        await dp.start_polling(bot)
