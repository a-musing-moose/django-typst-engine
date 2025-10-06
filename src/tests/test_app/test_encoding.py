import decimal
import uuid

import pytest
from tomlkit import exceptions

from django_typst import encoding


@pytest.mark.parametrize(
    "value, expected",
    [
        pytest.param(
            uuid.UUID("0c997d1c-080d-4b08-9d78-5922b3b75379"),
            "0c997d1c-080d-4b08-9d78-5922b3b75379",
            id="uuid",
        ),
        pytest.param(decimal.Decimal("12.99"), "12.99", id="decimal"),
    ],
)
def test_can_encode_stringy_types(value, expected):
    encoded = encoding._stringable_encoder(value)
    assert encoded == expected


def test_string_encoder_will_not_encode_other_types():
    with pytest.raises(exceptions.ConvertError):
        encoding._stringable_encoder(object())


def test_can_serialize_a_django_request_object(rf):
    request = rf.get("/some/path/or/other")

    encoded = encoding._request_encoder(request)
    assert encoded == {
        "path": "/some/path/or/other",
        "path_info": "/some/path/or/other",
        "method": "GET",
        "content_type": "",
        "content_params": {},
        "headers": {"Cookie": ""},
    }


def test_request_encoder_will_not_enocee_other_types():
    with pytest.raises(exceptions.ConvertError):
        encoding._request_encoder(object())
