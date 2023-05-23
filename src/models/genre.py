from pydantic import Field
from _orjson import Orjson


class Genre(Orjson):
    name: str
    description: str
    popularity: float = Field(gt=0, le=10)
