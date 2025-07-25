from fastapi import APIRouter

from . import (
    access,
    streams,
)


router = APIRouter()


router.include_router(access.router)
router.include_router(streams.router)


__all__ = [
    "router",
]
