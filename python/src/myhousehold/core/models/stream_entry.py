from __future__ import annotations

from typing import TYPE_CHECKING

from datetime import datetime

import jsonschema
from jsonschema.exceptions import ValidationError
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.dialects.postgresql import JSON

from myhousehold.core.exceptions import DomainValueError

from .base import Base

if TYPE_CHECKING:
    from . import Stream, User


class StreamEntry(Base):
    __tablename__ = "stream_entry"

    id: Mapped[int] = mapped_column(primary_key=True)
    json_data: Mapped[dict] = mapped_column(JSON())
    comment: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime | None]

    stream_id: Mapped[int] = mapped_column(ForeignKey("stream.id"))
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    stream: Mapped[Stream] = relationship()
    created_by_user: Mapped[User] = relationship()

    @validates("json_data")
    def validate_json_data(self, key, value):
        assert self.stream is not None, "Developer must ensure loading of this relationship"

        try:
            jsonschema.validate(value, self.stream.json_schema)
        except ValidationError as e:
            raise DomainValueError(
                detail="Json data schema does not match stream scheme",
            ) from e

        return value
