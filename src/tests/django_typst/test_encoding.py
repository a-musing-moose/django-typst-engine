import datetime
import decimal
import json
import uuid

import pytest
import tomlkit

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


def test_toml_context_encoder_serializes_shared_value_types(rf):
    request = rf.get("/some/path/or/other")
    context_encoder = encoding.TomlContextEncoder()

    encoded = tomlkit.loads(
        context_encoder.encode(
            {
                "price": decimal.Decimal("12.99"),
                "identifier": uuid.UUID("0c997d1c-080d-4b08-9d78-5922b3b75379"),
                "request": request,
            }
        )
    )

    assert encoded == {
        "price": "12.99",
        "identifier": "0c997d1c-080d-4b08-9d78-5922b3b75379",
        "request": {
            "path": "/some/path/or/other",
            "path_info": "/some/path/or/other",
            "method": "GET",
            "content_type": "",
            "content_params": {},
            "headers": {"Cookie": ""},
        },
    }


def test_toml_context_encoder_can_register_a_custom_value_encoder():
    class Widget:
        def __init__(self, code):
            self.code = code

    def widget_value_encoder(value):
        if isinstance(value, Widget):
            return value.code
        raise encoding.EncoderCannotHandleValue

    context_encoder = encoding.TomlContextEncoder()
    context_encoder.register_encoder(widget_value_encoder)

    encoded = tomlkit.loads(context_encoder.encode({"widget": Widget("abc-123")}))

    assert encoded == {"widget": "abc-123"}


def test_json_context_encoder_serializes_supported_value_types():
    context_encoder = encoding.JsonContextEncoder()

    encoded = json.loads(
        context_encoder.encode(
            {
                "name": "J Moss",
                "quantity": 3,
                "price": 12.99,
                "decimal": decimal.Decimal("12.99"),
                "identifier": uuid.UUID("0c997d1c-080d-4b08-9d78-5922b3b75379"),
                "date": datetime.date(2026, 9, 18),
                "time": datetime.time(9, 30),
                "datetime": datetime.datetime(2026, 9, 18, 9, 30, tzinfo=datetime.UTC),
                "items": ["one", 2],
                "metadata": {"published": True},
            }
        )
    )

    assert encoded == {
        "name": "J Moss",
        "quantity": 3,
        "price": 12.99,
        "decimal": "12.99",
        "identifier": "0c997d1c-080d-4b08-9d78-5922b3b75379",
        "date": "2026-09-18",
        "time": "09:30:00",
        "datetime": "2026-09-18T09:30:00+00:00",
        "items": ["one", 2],
        "metadata": {"published": True},
    }


def test_json_context_encoder_can_register_a_custom_value_encoder():
    class Widget:
        def __init__(self, code):
            self.code = code

    def widget_value_encoder(value):
        if isinstance(value, Widget):
            return value.code
        raise encoding.EncoderCannotHandleValue

    context_encoder = encoding.JsonContextEncoder()
    context_encoder.register_encoder(widget_value_encoder)

    encoded = json.loads(context_encoder.encode({"widget": Widget("abc-123")}))

    assert encoded == {"widget": "abc-123"}
