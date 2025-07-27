from deepdiff import DeepDiff
from pydantic import BaseModel

from .base import *  # noqa: F401, F403


def test_streams(
        client,
        authed_client,
):
    class DemoSchema(BaseModel):
        a: int

    # create demo schema
    req = api_templates.make_create_stream()
    req.json = {
        "name": "test",
        "json_schema": DemoSchema.model_json_schema(),
        "is_private": False,
    }
    r = client.prepsend(req)
    assert r.status_code == 401
    r = authed_client.prepsend(req)
    assert r.status_code == 201
    r_json = r.json()
    assert isinstance(r_json["id"], int)
    assert not DeepDiff(
        req.json, r_json,
        exclude_paths="root['id']",
    )
    val_stream_id = r_json["id"]

    # get streams
    req = api_templates.make_get_streams()
    r = client.prepsend(req)
    assert r.status_code == 401
    r = authed_client.prepsend(req)
    assert r.status_code == 200

    # create demo entry
    req = api_templates.make_create_stream_entry()
    req.path_params = {
        "stream_id": val_stream_id,
    }
    req.json = {
        "json_data": {"a": 5},
        "comment": None,
    }
    r = client.prepsend(req)
    assert r.status_code == 401
    r = authed_client.prepsend(req)
    assert r.status_code == 201
    assert r.json()

    req = api_templates.make_create_stream_entry()
    req.path_params = {
        "stream_id": val_stream_id,
    }
    req.json = {
        "json_data": {"a": "value-with-invalid-type"},
        "comment": None,
    }
    r = authed_client.prepsend(req)
    assert r.status_code == 422

    req = api_templates.make_get_stream_entries()
    req.path_params = {
        "stream_id": val_stream_id,
    }
    r = client.prepsend(req)
    assert r.status_code == 401
    r = authed_client.prepsend(req)
    assert r.status_code == 200
