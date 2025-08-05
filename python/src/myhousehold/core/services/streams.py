from collections.abc import Iterable
from typing import Any, Literal

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from myhousehold.core.models.intents.project import ProjectIntent
from myhousehold.core.models.intents.record import RecordIntent
from myhousehold.core.models.proposition import Proposition
from myhousehold.core.models.stream import Stream
from myhousehold.server.providers import AuthorizedUser


class StreamsServiceError(Exception):
    pass


class StreamNotFoundError(StreamsServiceError):
    pass


class StreamsService:
    def __init__(
            self,
            orm_session: AsyncSession,
            authorized_user: AuthorizedUser,
    ):
        self.orm_session = orm_session
        self.authorized_user = authorized_user

    async def create_stream(
            self,
            name: str,
            json_schema: dict[str, Any],
            is_private: bool,
            is_record_intent: Literal[True],
    ) -> Stream:
        assert is_record_intent
        stream = Stream(
            name=name,
            json_schema=json_schema,
            created_by_user_id=self.authorized_user.id,
            is_private=is_private,
            record_intent=RecordIntent(
                ttl=None,
                errata_allowed=True,
            ),
        )
        self.orm_session.add(stream)
        await self.orm_session.flush()

        return stream

    def _accessible_streams_stmt(self):
        stmt = (select(Stream)
                .where(
                    or_(Stream.created_by_user_id == self.authorized_user.id,
                        Stream.is_private.is_(False)))
                )
        return stmt

    async def get_streams(
            self,
    ) -> Iterable[Stream]:
        stmt = self._accessible_streams_stmt()
        return await self.orm_session.scalars(stmt)

    async def get_stream_with(
            self,
            id_: int | None = None,
            name: str | None = None,
    ) -> Stream | None:
        stmt = self._accessible_streams_stmt()

        if id_ is not None:
            stmt = stmt.where(Stream.id == id_)
        if name is not None:
            stmt = stmt.where(Stream.name == name)

        stream = await self.orm_session.scalar(stmt)
        return stream

    async def create_proposition(
            self,
            json_object: dict[str, Any],
            comment: str | None,
            stream: Stream,
    ) -> Proposition:
        proposition = Proposition(
            comment=comment,
            stream=stream,
            asserted_by_user=self.authorized_user,
        )
        proposition.json_object = json_object  # validation depends on stream
        self.orm_session.add(proposition)

        await self.orm_session.flush()

        return proposition

    async def put_stream_proposition(
            self,
            stream_id: int,
            proposition_id: int,
            json_object: dict[str, Any],
            comment: str | None,
    ) -> Proposition:
        stmt = (select(Proposition)
                .where(Proposition.stream_id == stream_id)
                .where(Proposition.id == proposition_id)
                .with_for_update()
                .options(joinedload(Proposition.stream)))
        proposition = await self.orm_session.scalar(stmt)

        if not proposition:
            stmt = self._accessible_streams_stmt()
            stmt = stmt.with_for_update()
            stream = await self.orm_session.scalar(stmt)
            if stream is None:
                raise StreamNotFoundError
            proposition = Proposition(
                json_object=json_object,
                comment=comment,
                asserted_by_user=self.authorized_user,
                stream=stream,
            )
            self.orm_session.add(proposition)
        else:
            proposition.json_object = json_object
            proposition.comment = comment

        await self.orm_session.flush()
        return proposition

    async def get_stream_propositions(
            self,
            stream_id: int,
    ) -> Iterable[Proposition]:
        # note: not used, but I want to test it
        stmt = select(Proposition)
        accessible_propositions = self._accessible_streams_stmt().subquery()
        stmt = (stmt
                .join_from(
                    accessible_propositions,
                    onclause=Proposition.stream_id
                             == accessible_propositions.c.id)
                .where(accessible_propositions.c.id == stream_id))
        scalars = await self.orm_session.scalars(stmt)
        return scalars.unique(lambda x: x.id)
