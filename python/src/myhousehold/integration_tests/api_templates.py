from typing import TYPE_CHECKING, Any

from requests import Request


_base_url = "http://rest-server"


class PatchedRequest(Request):
    path_params: dict[str, Any]

    if TYPE_CHECKING:
        def __init__(
                self,
                method=None,
                url=None,
                headers=None,
                files=None,
                data=None,
                params=None,
                auth=None,
                cookies=None,
                hooks=None,
                json=None,
                path_params: dict[str, Any] = None,
        ): ...
    else:
        def __init__(
                self,
                *args,
                path_params = None,
                **kwargs,
        ):
            super().__init__(*args, **kwargs)
            self.path_params = path_params or dict()


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
