""" Схема для api/v1/movie """
import uuid

from models._orjson import Orjson


class MovieShort(Orjson):
    uuid: uuid.UUID
    imdb_rating: float | None
    title: str

    class Config:
        json_encoders = {
            uuid.UUID: lambda u: str(u),
        }
