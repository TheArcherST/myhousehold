from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import jsonschema
from jsonschema.exceptions import ValidationError
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from myhousehold.core.exceptions import DomainValueError

from .base import Base

if TYPE_CHECKING:
    from . import Stream, User


class Proposition(Base):
    __tablename__ = "proposition"

    id: Mapped[int] = mapped_column(primary_key=True)
    json_object: Mapped[dict] = mapped_column(JSON())
    comment: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime | None]

    stream_id: Mapped[int] = mapped_column(ForeignKey("stream.id"))
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    stream: Mapped[Stream] = relationship()
    asserted_by_user: Mapped[User] = relationship()

    @validates("json_object")
    def validate_json_object(self, key, value):
        assert self.stream is not None, \
            "Developer must ensure loading of this relationship"

        try:
            jsonschema.validate(value, self.stream.json_schema)
        except ValidationError as e:
            raise DomainValueError(
                detail="JSON data does not match JSON schema of the stream",
            ) from e

        return value
