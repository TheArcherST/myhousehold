from pydantic import JsonValue

from .base import BaseDTO


class CreateStreamDTO(BaseDTO):
    name: str
    json_schema: dict[str, JsonValue]
    is_private: bool


class StreamDTO(BaseDTO):
    id: int
    name: str
    json_schema: dict[str, JsonValue]
    is_private: bool


class CreateStreamEntryDTO(BaseDTO):
    json_data: dict[str, JsonValue]
    comment: str | None


class StreamEntryDTO(BaseDTO):
    id: int
    json_data: dict[str, JsonValue]
    comment: str | None
