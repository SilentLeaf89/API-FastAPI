""" Схема для api/v1/movie """
from typing import List, Optional
import uuid

from models._orjson import Orjson
from models.role import Role
from models.movie import GenreShort


class MovieInfo(Orjson):
    uuid: uuid.UUID
    title: str
    imdb_rating: float | None
    description: Optional[str]
    genre: List[GenreShort]
    actors: Optional[List[Role]]
    writers: Optional[List[Role]]
    directors: Optional[List[Role]]

    class Config:
        json_encoders = {
            uuid.UUID: lambda u: str(u),
            Role: lambda s: str(s),
            GenreShort: lambda s: str(s),
        }
