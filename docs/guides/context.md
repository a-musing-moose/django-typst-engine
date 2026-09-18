# Handling Context

Context data passed into the template is first encoded in [TOML] format. Note this means
that only data types that can be serialized as TOML can be passed as context variables.
We use [tomlkit] to serialize the context. In practice this means the following types
can be included in the context:

- `str`
- `int`
- `float`
- `bool`
- `datetime.datetime`, `.time`, and `.date`
- `list`
- `dict`

In addition to these types, you can also include `decimal.Decimal`, `uuid.UUID` objects,
which are rendered to strings before serializing.

There is also special handling for the Django `HTTPRequest` object, which is converted
to a dict before serializing. The contents of that dict are:

```python
{
    "path": request.path,
    "path_info": request.path_info,
    "method": request.method,
    "content_type": request.content_type,
    "content_params": request.content_params,
    "headers": {},  # header-name: header-value
}
```

To then make use of context within a Typst template you must parse the incoming TOML
data by adding the following to the top of the Typst file:

```typst
#let ctx = toml(bytes(sys.inputs.context))
```

This will deserialize the context and assign it to the Typst variable `ctx` which can
then be used in the template like any other variable. For example if you context was
something like:

```python
{
  "name": "J Moss",
  "flight": "QF1",
}
```

Then in your template you will be able to reference it with:

```typst
#ctx.name your flight number is #ctx.flight
```

Or even better is to parse the context as follows:

```typst
// Parse context or use defaults
#let ctx = if ("context" in sys.inputs) {
  toml(bytes(sys.inputs.context))
} else {
  (
    "name": "A Citizen",
    "flight": "DL31"
  )
}
```

This version sets a default if `context` isn't passed in. This allows you to test the
template in isolation - say with the [Tinymist] Extension to VSCode or even just running
`typst` directly on it.

## Extending TOML Serialization

If you want the serialization to transparently handle addition types you can register
custom encoder functions with tomlkit.

For example the follow code snippet would add handling of a type called `Widget` that
has a `code` property.

```python
import tomlkit
from tomlkit import exceptions, items


def widget_encoder(o: typing.Any) -> items.Item:
    """
    A tomlkit encoder for objects that should just be serialized as strings
    """
    if isinstance(o, Widget):
        return items.String.from_raw(str(widget.code))
    raise exceptions.ConvertError

tomlkit.register_encoder(widget_encoder)
```

Note the at the end of the snippet above, there is an explicit registration of the new
widget encoder. You must make sure that the code executes the registration before you
can use it.

Take a look at [`django_typst/encoding.py`][encoding] for more examples.

<!-- Links -->

[encoding]: https://github.com/a-musing-moose/django-typst-engine/blob/main/src/django_typst/encoding.py
[tinymist]: https://github.com/Myriad-Dreamin/tinymist
[toml]: https://toml.io/en/
[tomlkit]: https://tomlkit.readthedocs.io/en/latest/
