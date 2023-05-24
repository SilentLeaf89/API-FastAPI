import uuid

from models._orjson import Orjson


class Role(Orjson):
    id: uuid.UUID
    full_name: str
