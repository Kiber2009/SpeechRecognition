import tempfile
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    INCLUDE_BACKENDS: list[str] | None = None
    CONVERTER: str
    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_PROXY: str | None = None
    TEMP_DIR: Path = Path(tempfile.gettempdir()) / "SpeechRecognition"
    MODELS_DIR: Path

    @field_validator("INCLUDE_BACKENDS", mode="before")
    @classmethod
    def load_list(cls, v):
        if isinstance(v, str):
            return v.split(";")
        return v

    @property
    def download_dir(self) -> Path:
        return self.TEMP_DIR / "download"



# noinspection PyArgumentList
SETTINGS = Settings()
