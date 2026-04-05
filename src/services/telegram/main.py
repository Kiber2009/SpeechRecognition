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
    data: Voice | VideoNote | Video | Audio,
    message: Message,
    extension: str | None = None,
) -> None:
    answer: Message = await message.reply("Распознаю речь\nПожалуйста подождите")

    if data.file_size > MAX_FILE_SIZE:
        await answer.edit_text("Сообщение слишком большое")
        return

    with TemporaryFile("w+b", dir=DOWNLOAD_DIR, delete_on_close=False) as tmp:
        # noinspection PyTypeChecker
        await bot.download_file(
            (await bot.get_file(data.file_id)).file_path,
            destination=tmp,
        )
        tmp.seek(0)
        if extension is None:
            extension = filetype.guess(tmp.read(261)).extension

        logging.debug(tmp.name)
        back = select_backend(languages=(message.from_user.language_code,))
        res_path, res_type = await convert(
            Path(tmp.name),
            extension,
            *back.supported_formats,
        )

    res = await back.process(res_path, res_type)
    await answer.edit_text(res)

    # os.remove(tmp.name)
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
