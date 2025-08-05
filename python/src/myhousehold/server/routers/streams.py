from collections.abc import Iterable

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, HTTPException, status

from myhousehold.core.models import Proposition
from myhousehold.core.models.stream import Stream
from myhousehold.core.services.streams import StreamsService
from myhousehold.core.services.uow_ctl import UoWCtl
from myhousehold.server.schemas.streams import (
    CreateStreamDTO,
    CreateStreamPropositionDTO,
    StreamDTO,
    StreamPropositionDTO,
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
        is_record_intent=True,
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
    "/{stream_id}/propositions",
    response_model=StreamPropositionDTO,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_stream_proposition(
        streams_service: FromDishka[StreamsService],
        uow_ctl: FromDishka[UoWCtl],
        stream_id: int,
        payload: CreateStreamPropositionDTO,
) -> Proposition:
    stream = await streams_service.get_stream_with(
        id_=stream_id,
    )
    if stream is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found",
        )

    proposition = await streams_service.create_proposition(
        json_object=payload.json_object,
        comment=payload.comment,
        stream=stream,
    )

    await uow_ctl.commit()

    return proposition


@router.get(
    "/{stream_id}/propositions",
    response_model=list[StreamPropositionDTO],
)
@inject
async def get_stream_propositions(
        streams_service: FromDishka[StreamsService],
        stream_id: int,
) -> Iterable[Proposition]:
    stream = await streams_service.get_stream_with(
        id_=stream_id,
    )
    return stream.propositions


@router.put(
    "/{stream_id}/propositions/{proposition_id}",
    response_model=StreamPropositionDTO,
)
@inject
async def put_stream_proposition(
        streams_service: FromDishka[StreamsService],
        uow_ctl: FromDishka[UoWCtl],
        stream_id: int,
        proposition_id: int,
        payload: CreateStreamPropositionDTO,
) -> Proposition:
    proposition = await streams_service.put_stream_proposition(
        stream_id=stream_id,
        proposition_id=proposition_id,
        json_object=payload.json_object,
        comment=payload.comment,
    )
    if proposition is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream or entry not found",
        )

    await uow_ctl.commit()

    return proposition
