import uuid
from pydantic import Field
from models._orjson import Orjson


class Genre(Orjson):
    id: uuid.UUID
    name: str
    description: str
    popularity: float = Field(gt=0, le=10)
