from datetime import datetime
from pathlib import Path
from typing import List, Optional
import uuid

from pydantic import Field

from models._orjson import Orjson
from models.role import Role


class Movie(Orjson):
    id: uuid.UUID
    imdb_rating: float | None
    genre: List[str] = Field(None, alias='genres_field')
    title: str
    creation_date: datetime
    description: Optional[str]
    director: Optional[List[str]]
    actors_names: Optional[List[str]]
    writers_names: Optional[List[str]]
    actors: Optional[List[Role]]  # возможно убрать
    writers: Optional[List[Role]]  # возможно убрать
    link: Path

    class Config:
        json_encoders = {
            uuid.UUID: lambda u: str(u),
            datetime: lambda v: v.timestamp(),
            Role: lambda s: str(s),
        }


class ShortMovie(Orjson):
    id: uuid.UUID
    imdb_rating: float | None
    title: str

    class Config:
        json_encoders = {
            uuid.UUID: lambda u: str(u),
        }


class RoleMovie(Orjson):
    id: uuid.UUID
    roles: List[str]

    class Config:
        json_encoders = {
            uuid.UUID: lambda u: str(u),
        }
