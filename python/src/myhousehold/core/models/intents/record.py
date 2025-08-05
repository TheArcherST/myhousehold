from datetime import timedelta

from sqlalchemy.orm import Mapped

from .base import BaseIntent


class RecordIntent(BaseIntent):
    """ Intent of recording """

    __tablename__ = "record_intent"

    ttl: Mapped[timedelta | None]
    errata_allowed: Mapped[bool]
