from abc import ABC, abstractmethod
from typing import Annotated

from pydantic import BaseModel, Field

from backends import Backend
from utils import DynamicUnionType, ValueStore


class ModelConfig(BaseModel, ABC):
    @abstractmethod
    def get_backend(self) -> Backend:
        pass


model_config_types: DynamicUnionType[ModelConfig] = DynamicUnionType()


class ConfigTemplate(BaseModel):
    models: dict[str, ModelConfig]


def make_config() -> type[ConfigTemplate]:
    config_types = Annotated[model_config_types.get(), Field(discriminator="type")]

    class Config(BaseModel):
        models: dict[str, config_types]

    return Config


config = ValueStore[ConfigTemplate]()


def load_config(data: str | bytes | bytearray) -> None:
    config.set(make_config().model_validate_json(data))
