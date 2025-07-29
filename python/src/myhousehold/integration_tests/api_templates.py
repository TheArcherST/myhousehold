from myhousehold.integration_tests.base import PatchedRequest

_base_url = "http://rest-server"  # docker compose address

def make_create_stream():
    return PatchedRequest(
        method="POST",
        url=_base_url + "/streams",
    )

def make_get_streams():
    return PatchedRequest(
        method="GET",
        url=_base_url + "/streams",
    )

def make_create_stream_entry():
    return PatchedRequest(
        method="POST",
        url=_base_url + "/streams/{stream_id}/entries",
    )

def make_get_stream_entries():
    return PatchedRequest(
        method="GET",
        url=_base_url + "/streams/{stream_id}/entries",
    )

def make_register():
    return PatchedRequest(
        method="POST",
        url=_base_url + "/register",
    )

def make_login():
    return PatchedRequest(
        method="POST",
        url=_base_url + "/login",
    )
