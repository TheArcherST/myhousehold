from enum import StrEnum

from sqlalchemy.orm import Mapped

from myhousehold.core.models.intents.base import BaseIntent


class Urgency(StrEnum):
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"


class ProjectIntent(BaseIntent):
    """ Intent of projection """

    __tablename__ = "project_intent"

    urgency: Mapped[Urgency]
    is_instant: Mapped[bool]
