from fastapi import FastAPI, Request, HTTPException, Response

from myhousehold.core.exceptions import DomainValueError


async def domain_value_error_handler(request: Request, exc: DomainValueError) -> Response:
    raise HTTPException(
        status_code=422,
        detail=exc.detail,
    )


def register(app: FastAPI):
    app.add_exception_handler(DomainValueError, domain_value_error_handler)
