from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class BaseIntent(Base):
    """ Describes verb predicate of object in a proposition """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
