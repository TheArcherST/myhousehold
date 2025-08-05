from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import jsonschema
from jsonschema.exceptions import SchemaError
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from .proposition import Proposition
from ..exceptions import DomainValueError
from .base import Base
from .intents.project import ProjectIntent
from .intents.record import RecordIntent

if TYPE_CHECKING:
    from . import Proposition


class Stream(Base):
    """ Collection of typed propositions """

    # todo: think about differentiation of propositions types and streams

    __tablename__ = "stream"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    json_schema: Mapped[dict] = mapped_column(JSON())
    is_private: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    record_intent_id: Mapped[int | None] = mapped_column(
        ForeignKey("record_intent.id"),
    )
    project_intent_id: Mapped[int | None] = mapped_column(
        ForeignKey("project_intent.id"),
    )
    created_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
    )

    record_intent: Mapped[RecordIntent | None] = relationship()
    project_intent: Mapped[ProjectIntent | None] = relationship()
    propositions: Mapped[list[Proposition]] = relationship(
        lazy="selectin",
    )

    @validates
    def validate_json_schema(self, key, value):
        try:
            (jsonschema.validators
             .validator_for(value)
             .check_schema(value))
        except SchemaError as e:
            raise DomainValueError(
                detail="Invalid JSON schema",
            ) from e
