from typing import Any

from .base import BaseDTO


class CreateStreamDTO(BaseDTO):
    name: str
    json_schema: dict[str, Any]
    is_private: bool


class StreamDTO(BaseDTO):
    id: int
    name: str
    json_schema: dict[str, Any]
    is_private: bool


class CreateStreamEntryDTO(BaseDTO):
    json_data: dict[str, Any]
    comment: str | None


class StreamEntryDTO(BaseDTO):
    id: int
    json_data: dict[str, Any]
    comment: str | None
