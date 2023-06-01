""" Модель, получаемая из индекса elasticsearch: "person" """

import uuid

from models._orjson import Orjson


class Role(Orjson):
    id: uuid.UUID
    full_name: str

    class Config:
        json_encoders = {
            uuid.UUID: lambda u: str(u)
        }
