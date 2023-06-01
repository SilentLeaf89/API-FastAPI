""" Модель, получаемая из индекса elasticsearch: "movies" """

from typing import List, Optional
import uuid

from models._orjson import Orjson
from models.role import Role


class GenreShort(Orjson):
    id: uuid.UUID
    name: str

    class Config:
        json_encoders = {
            uuid.UUID: lambda u: str(u),
        }


class Movie(Orjson):
    id: uuid.UUID
    imdb_rating: float | None
    genre_name: List[str]
    genre: List[GenreShort]
    title: str
    description: Optional[str]
    director: Optional[List[str]]
    actors_names: Optional[List[str]]
    writers_names: Optional[List[str]]
    actors: Optional[List[Role]]
    writers: Optional[List[Role]]
    directors: Optional[List[Role]]

    class Config:
        json_encoders = {
            uuid.UUID: lambda u: str(u),
            Role: lambda s: str(s),
        }
