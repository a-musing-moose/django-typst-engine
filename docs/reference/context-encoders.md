# Context encoders

A context encoder serializes Django template context data into the string passed
to Typst as `sys.inputs.context`. The Typst template must deserialize the string
with the matching Typst function.

## Interface

Every encoder subclasses `django_typst.encoding.ContextEncoder` and implements
`encode`, which accepts a context value and returns a string. The TOML, JSON, and
YAML encoders accept dictionaries. The CSV encoder accepts a list of mappings.

```python
from django_typst.encoding import ContextEncoder


class WidgetContextEncoder(ContextEncoder):
    def encode(self, context: dict[str, object]) -> str:
        prepared_context = self.encode_value(context)
        return serialize_widgets(prepared_context)
```

`encode_value` recursively processes dictionaries and lists. It calls the
converters registered with `register_encoder` for each non-container value.
Converters return a replacement value or raise `EncoderCannotHandleValue` when
the value isn't theirs to convert.

```python
from typing import Any

from django_typst.encoding import EncoderCannotHandleValue


def widget_value_encoder(value: Any) -> str:
    if isinstance(value, Widget):
        return value.code
    raise EncoderCannotHandleValue


encoder = WidgetContextEncoder()
encoder.register_encoder(widget_value_encoder)
```

Converter registrations belong to an encoder instance. Register a converter on
the instance that the Django template engine uses. Configure the class with the
`CONTEXT_ENCODER` option, which accepts a dotted class path. Built-in encoders reuse
`register_default_value_encoders`, which provides conversions for `Decimal`,
`UUID`, and Django `HttpRequest` objects.

## Context values

All built-in encoders support `str`, `int`, `float`, `Decimal`, `UUID`, `date`,
`time`, `datetime`, `list`, and `dict`. `Decimal` and `UUID` are represented as
strings. TOML preserves its native temporal types. JSON, YAML, and CSV represent
`date`, `time`, and `datetime` as ISO 8601 strings.

CSV is tabular only. Its context is a list of uniform, flat mappings; values in
a CSV cell can't be a dictionary or list.

## Parsing in Typst

Built-in encoders use the corresponding Typst function:

```typst
#let ctx = toml(bytes(sys.inputs.context))
#let ctx = json(bytes(sys.inputs.context))
#let ctx = yaml(bytes(sys.inputs.context))
#let ctx = csv(bytes(sys.inputs.context))
```

Use the expression that matches the configured encoder. The CSV result is a
table rather than a general dictionary.
