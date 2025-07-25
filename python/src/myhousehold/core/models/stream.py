from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSON

from .base import Base

if TYPE_CHECKING:
    from . import StreamEntry


class Stream(Base):
    __tablename__ = "stream"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    json_schema: Mapped[dict] = mapped_column(JSON())
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    is_private: Mapped[bool]

    entries: Mapped[list[StreamEntry]] = relationship(
        lazy="selectin",
    )
