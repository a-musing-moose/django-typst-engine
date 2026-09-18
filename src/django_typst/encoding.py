import abc
import decimal
import typing
import uuid

import tomlkit
from django import http


class EncoderCannotHandleValue(Exception):
    """
    Raised by a value encoder when it cannot convert the supplied value.
    """


ContextValueEncoder = typing.Callable[[typing.Any], typing.Any]


class ContextEncoder(abc.ABC):
    """
    Serializes a Django template context for consumption by Typst.
    """

    def __init__(self) -> None:
        self._value_encoders: list[ContextValueEncoder] = []

    @abc.abstractmethod
    def encode(self, context: dict[str, typing.Any]) -> str:
        """
        Serialize a context into the format understood by this encoder.
        """

    def register_encoder(self, encoder: ContextValueEncoder) -> None:
        """
        Register an instance-specific conversion for unsupported values.
        """
        self._value_encoders.append(encoder)

    def encode_value(self, value: typing.Any) -> typing.Any:
        """
        Recursively apply registered conversions to a context value.
        """
        if isinstance(value, dict):
            mapping = typing.cast(dict[str, typing.Any], value)
            return {key: self.encode_value(item) for key, item in mapping.items()}
        if isinstance(value, list):
            return [self.encode_value(item) for item in value]

        for encoder in self._value_encoders:
            try:
                return self.encode_value(encoder(value))
            except EncoderCannotHandleValue:
                continue

        return value


def stringable_value_encoder(value: typing.Any) -> str:
    """
    Convert values represented as strings by every built-in context encoder.
    """
    if isinstance(value, (decimal.Decimal, uuid.UUID)):
        return str(value)
    raise EncoderCannotHandleValue


def request_value_encoder(value: typing.Any) -> dict[str, typing.Any]:
    """
    Convert Django HttpRequest objects into a context mapping.
    """
    if isinstance(value, http.HttpRequest):
        return {
            "path": value.path,
            "path_info": value.path_info,
            "method": value.method,
            "content_type": value.content_type,
            "content_params": value.content_params,
            "headers": {key: item for key, item in value.headers.items()},
        }
    raise EncoderCannotHandleValue


def register_default_value_encoders(encoder: ContextEncoder) -> None:
    """
    Register the value conversions shared by built-in context encoders.
    """
    encoder.register_encoder(stringable_value_encoder)
    encoder.register_encoder(request_value_encoder)


class TomlContextEncoder(ContextEncoder):
    """
    Serialize a Django template context as TOML.
    """

    def __init__(self) -> None:
        super().__init__()
        register_default_value_encoders(self)

    def encode(self, context: dict[str, typing.Any]) -> str:
        return tomlkit.dumps(self.encode_value(context))
