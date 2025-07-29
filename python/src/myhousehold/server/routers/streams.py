from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, HTTPException, status

from myhousehold.core.models.stream import Stream
from myhousehold.core.models.stream_entry import StreamEntry
from myhousehold.core.services.streams import StreamsService
from myhousehold.core.services.uow_ctl import UoWCtl
from myhousehold.server.schemas.streams import (
    CreateStreamDTO,
    CreateStreamEntryDTO,
    StreamDTO,
    StreamEntryDTO,
)

router = APIRouter(
    prefix="/streams",
)


@router.post(
    "",
    response_model=StreamDTO,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_stream(
        streams_service: FromDishka[StreamsService],
        uow_ctl: FromDishka[UoWCtl],
        payload: CreateStreamDTO,
) -> Stream:
    stream = await streams_service.create_stream(
        name=payload.name,
        json_schema=payload.json_schema,
        is_private=payload.is_private,
    )
    await uow_ctl.commit()
    return stream


@router.get(
    "",
    response_model=list[StreamDTO],
)
@inject
async def get_streams(
        streams_service: FromDishka[StreamsService],
) -> list[Stream]:
    streams = await streams_service.get_streams()
    streams = list(streams)
    return streams


@router.post(
    "/{stream_id}/entries",
    response_model=StreamEntryDTO,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_stream_entry(
        streams_service: FromDishka[StreamsService],
        uow_ctl: FromDishka[UoWCtl],
        stream_id: int,
        payload: CreateStreamEntryDTO,
) -> StreamEntry:
    stream = await streams_service.get_stream_with(
        id_=stream_id,
    )
    if stream is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found",
        )

    entry = await streams_service.create_stream_entry(
        json_data=payload.json_data,
        comment=payload.comment,
        stream=stream,
    )

    await uow_ctl.commit()

    return entry


@router.get(
    "/{stream_id}/entries",
    response_model=list[StreamEntryDTO],
)
@inject
async def get_stream_entries(
        streams_service: FromDishka[StreamsService],
        stream_id: int,
):
    stream = await streams_service.get_stream_with(
        id_=stream_id,
    )
    return stream.entries


@router.put(
    "/{stream_id}/entries/{entry_id}",
    response_model=StreamEntryDTO,
)
@inject
async def put_stream_entry(
        streams_service: FromDishka[StreamsService],
        uow_ctl: FromDishka[UoWCtl],
        stream_id: int,
        entry_id: int,
        payload: CreateStreamEntryDTO,
) -> StreamEntry:
    entry = await streams_service.put_stream_entry(
        stream_id=stream_id,
        entry_id=entry_id,
        json_data=payload.json_data,
        comment=payload.comment,
    )
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream or entry not found",
        )

    await uow_ctl.commit()

    return entry
