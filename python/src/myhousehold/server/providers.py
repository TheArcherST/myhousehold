import uuid
from typing import NewType
from uuid import UUID

from dishka import Provider, provide, Scope, from_context
from fastapi import HTTPException, FastAPI
from fastapi.requests import Request

from starlette.testclient import TestClient

from myhousehold.core.models import User, LoginSession
from myhousehold.core.services.access import AccessService, ErrorUnauthorized


AuthorizedUser = NewType("AuthorizedUser", User)
CurrentLoginSession = NewType("CurrentLoginSession", LoginSession)


class ProviderServer(Provider):
    app = from_context(FastAPI, scope=Scope.SESSION)
    request = from_context(provides=Request, scope=Scope.REQUEST)

    @provide(scope=Scope.SESSION, cache=False)
    def get_test_client(self, app: FastAPI) -> TestClient:
        return TestClient(app)

    @provide(scope=Scope.REQUEST)
    async def get_current_login_session(
            self,
            request: Request,
            access_service: AccessService,
    ) -> CurrentLoginSession:
        try:
            login_session = await access_service.lookup_login_session(
                login_session_uid=UUID(request.headers.get("X-Login-Session-Uid", str(uuid.uuid4()))),
                login_session_token=request.headers.get("X-Login-Session-Token", "stub-token"),
            )
        except ErrorUnauthorized:
            raise HTTPException(status_code=401, detail="Invalid login session")

        return CurrentLoginSession(login_session)

    @provide(scope=Scope.REQUEST)
    async def get_authorized_user(
            self,
            current_login_session: CurrentLoginSession,
    ) -> AuthorizedUser:
        return AuthorizedUser(current_login_session.user)

    get_access_service = provide(
        AccessService,
        scope=Scope.REQUEST,
    )
