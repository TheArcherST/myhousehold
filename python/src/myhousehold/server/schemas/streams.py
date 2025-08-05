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


class CreateRecordIntent(BaseDTO):
    pass


class CreateStreamPropositionDTO(BaseDTO):
    json_object: dict[str, JsonValue]
    comment: str | None


class StreamPropositionDTO(BaseDTO):
    id: int
    json_object: dict[str, JsonValue]
    comment: str | None
