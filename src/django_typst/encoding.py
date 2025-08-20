import decimal
import typing
import uuid

import tomlkit
from django import http
from tomlkit import exceptions, items


def _stringable_encoder(o: typing.Any) -> items.Item:
    """
    A tomlkit encoder for objects that should just be serialized as strings
    """
    if isinstance(o, (decimal.Decimal, uuid.UUID)):
        return items.String.from_raw(str(o))
    raise exceptions.ConvertError


def _request_encoder(o: typing.Any) -> items.Item:
    """
    A tomlkit encoder for the Django HttpRequest object
    """
    if isinstance(o, http.HttpRequest):
        encoded_request = tomlkit.table()
        encoded_request.update(
            {
                "path": o.path,
                "path_info": o.path_info,
                "method": o.method,
                "content_type": o.content_type,
                "content_params": o.content_params,
                "headers": {k: v for k, v in o.headers.items()},
                # TODO: Add GET/POST/META
            }
        )
        return encoded_request
    raise exceptions.ConvertError


def register_encoders() -> None:
    tomlkit.register_encoder(_stringable_encoder)
    tomlkit.register_encoder(_request_encoder)
