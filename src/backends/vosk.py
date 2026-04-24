import json
import logging
import wave
from pathlib import Path
from typing import Iterable, Literal

from vosk import KaldiRecognizer, Model

from backends import Backend
from config import ModelConfig

logger = logging.getLogger(__name__)


class VoskModelConfig(ModelConfig):
    type: Literal["vosk"]
    path: Path
    languages: list[str]

    def get_backend(self) -> Backend:
        return VoskBackend(self.path, *self.languages)


class VoskBackend(Backend):
    def __init__(self, path: Path, *lang: str) -> None:
        self.model = None
        self.path = path
        self.lang = lang

    @property
    def supported_formats(self) -> Iterable[str]:
        return ("wav",)

    @property
    def supported_languages(self) -> Iterable[str]:
        return self.lang

    async def setup(self) -> None:
        path = self.path.absolute()
        logger.debug(f'Loading vosk model "{path}"')
        self.model = Model(str(path))

    async def process(self, file: Path, media_type: str) -> str:
        if media_type != "wav":
            raise ValueError("Vosk requires wav media type")

        with wave.open(str(file), "rb") as wf:
            rec = KaldiRecognizer(self.model, wf.getframerate())
            rec.SetWords(True)
            rec.SetPartialWords(True)

            while True:
                data = wf.readframes(wf.getnframes())
                if len(data) == 0:
                    break
                rec.AcceptWaveform(data)

            return json.loads(rec.FinalResult())["text"]
