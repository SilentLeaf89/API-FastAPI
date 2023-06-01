""" Схема для api/v1//person/{uuid} """

from typing import List
import uuid

from models._orjson import Orjson


class MovieRoles(Orjson):
    # id фильма
    uuid: uuid.UUID
    # список ролей персоны в указанном фильме ['actor', 'writer']
    roles: List[str]

    class Config:
        json_encoders = {
            uuid.UUID: lambda u: str(u),
        }


class Person(Orjson):
    uuid: uuid.UUID
    full_name: str
    movies: List[MovieRoles]

    class Config:
        json_encoders = {
            uuid.UUID: lambda u: str(u),
            MovieRoles: lambda s: str(s),
        }
