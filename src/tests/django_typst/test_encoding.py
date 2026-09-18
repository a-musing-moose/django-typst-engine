import decimal
import uuid

import pytest
from tomlkit import exceptions

from django_typst import encoding


class StubContextEncoder(encoding.ContextEncoder):
    def encode(self, context):
        return str(self.encode_value(context))


def test_context_encoder_applies_registered_conversions_recursively():
    context_encoder = StubContextEncoder()
    context_encoder.register_encoder(encoding.stringable_value_encoder)

    encoded = context_encoder.encode_value(
        {
            "price": decimal.Decimal("12.99"),
            "identifiers": [uuid.UUID("0c997d1c-080d-4b08-9d78-5922b3b75379")],
        }
    )

    assert encoded == {
        "price": "12.99",
        "identifiers": ["0c997d1c-080d-4b08-9d78-5922b3b75379"],
    }


def test_context_encoder_registrations_are_instance_specific():
    registered_encoder = StubContextEncoder()
    registered_encoder.register_encoder(encoding.stringable_value_encoder)
    unregistered_encoder = StubContextEncoder()

    value = decimal.Decimal("12.99")

    assert registered_encoder.encode_value(value) == "12.99"
    assert unregistered_encoder.encode_value(value) == value


def test_request_value_encoder_can_encode_a_django_request_object(rf):
    request = rf.get("/some/path/or/other")

    encoded = encoding.request_value_encoder(request)

    assert encoded == {
        "path": "/some/path/or/other",
        "path_info": "/some/path/or/other",
        "method": "GET",
        "content_type": "",
        "content_params": {},
        "headers": {"Cookie": ""},
    }


def test_value_encoder_signals_when_it_cannot_handle_a_value():
    with pytest.raises(encoding.EncoderCannotHandleValue):
        encoding.stringable_value_encoder(object())


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
