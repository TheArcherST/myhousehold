from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSON

from .base import Base


class StreamEntry(Base):
    __tablename__ = "stream_entry"

    id: Mapped[int] = mapped_column(primary_key=True)
    json_data: Mapped[dict] = mapped_column(JSON())
    comment: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime | None]

    stream_id: Mapped[int] = mapped_column(ForeignKey("stream.id"))
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
