import uuid
from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .user import User

from .base import Base


class LoginSession(Base):
    __tablename__ = "login_session"

    uid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_agent: Mapped[str | None]
    token: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    user: Mapped[User] = relationship(lazy="joined")
