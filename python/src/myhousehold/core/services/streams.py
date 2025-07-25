from typing import Any, Iterable

from sqlalchemy import select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession

from myhousehold.core.models.stream import Stream
from myhousehold.core.models.stream_entry import StreamEntry
from myhousehold.server.providers import AuthorizedUser


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
    ) -> Stream:
        stream = Stream(
            name=name,
            json_schema=json_schema,
            created_by_user_id=self.authorized_user.id,
            is_private=is_private,
        )
        self.orm_session.add(stream)
        await self.orm_session.flush()

        return stream

    def _accessible_streams_stmt(self):
        stmt = (select(Stream)
                .where(or_(Stream.created_by_user_id == self.authorized_user.id,
                           Stream.is_private.is_(False))))
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

    async def create_stream_entry(
            self,
            stream: Stream,
            json_data: dict[str, Any],
            comment: str | None,
    ) -> StreamEntry:
        entry = StreamEntry(
            json_data=json_data,
            comment=comment,
            created_by_user_id=self.authorized_user.id,
        )
        stream.entries.append(entry)
        await self.orm_session.flush()

        return entry

    async def put_stream_entry(
            self,
            stream_id: int,
            entry_id: int,
            json_data: dict[str, Any],
            comment: str,
            is_private: bool,
    ) -> StreamEntry:
        stmt = (
            update(StreamEntry)
            .where(StreamEntry.stream_id == stream_id)
            .where(StreamEntry.id == entry_id)
            .values(
                json_data=json_data,
                comment=comment,
                is_private=is_private,
            )
            .returning(StreamEntry)
        )
        entry = await self.orm_session.scalar(stmt)
        return entry

    async def get_stream_entries(
            self,
            stream_id: int,
    ) -> Iterable[StreamEntry]:
        # note: not used, but I want to test it
        stmt = select(StreamEntry)
        accessible_streams = self._accessible_streams_stmt().subquery()
        stmt = (stmt
                .join_from(
                    accessible_streams,
                    onclause=StreamEntry.stream_id == accessible_streams.c.id)
                .where(accessible_streams.c.id == stream_id))
        scalars = await self.orm_session.scalars(stmt)
        return scalars.unique(lambda x: x.id)
