import copy
from uuid import uuid4

import pytest
from requests import Session, Request

from myhousehold.integration_tests.api_templates import PatchedRequest

from . import api_templates


class PatchedSession(Session):
    def prepsend(self, request: Request, *args, **kwargs):
        kwargs.setdefault("verify", False)

        if isinstance(request, PatchedRequest):
            request.url = request.url.format(**request.path_params)

        return self.send(
            self.prepare_request(request),
            *args,
            **kwargs,
        )


@pytest.fixture()
def client() -> PatchedSession:
    client = PatchedSession()
    return client


@pytest.fixture()
def authed_client() -> PatchedSession:
    client = PatchedSession()
    req = api_templates.make_register()
    val_username = f"test_user-{uuid4()}"
    val_password = "test_user_password"
    req.json = {
        "username": val_username,
        "password": val_password,
    }
    r = client.prepsend(req)
    assert r.status_code == 201
    req = api_templates.make_login()
    req.json = {
        "username": val_username,
        "password": val_password,
    }
    r = client.prepsend(req)
    assert r.status_code == 201
    authorization_creds = r.json()
    client.headers["X-Login-Session-Uid"] = authorization_creds["login_session_uid"]
    client.headers["X-Login-Session-Token"] = authorization_creds["login_session_token"]
    pass

    return client
