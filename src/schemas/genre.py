""" Схема для api/v1/genres """
from typing import Optional
import uuid

from models._orjson import Orjson


class Genre(Orjson):
    uuid: uuid.UUID
    name: str
    description: Optional[str]

    class Config:
        json_encoders = {
            uuid.UUID: lambda u: str(u),
        }
