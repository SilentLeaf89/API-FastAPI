import uuid
from typing import List

from _orjson import Orjson

from models.movie import Movie


class Role(Orjson):
    id: uuid.UUID
    name: str
    movie: List[Movie]
