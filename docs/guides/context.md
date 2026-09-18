# Handling Context

Context data passed into a template is serialized to a string and provided to Typst
as `sys.inputs.context`. TOML is the default format. Set `CONTEXT_ENCODER` in the
Django template engine options to select a different encoder class.

```python
"OPTIONS": {
  "CONTEXT_ENCODER": "django_typst.encoding.JsonContextEncoder",
}
```

The built-in encoder classes are:

| Encoder | Typst parser | Context shape |
| --- | --- | --- |
| `TomlContextEncoder` | `toml(bytes(sys.inputs.context))` | Dictionary |
| `JsonContextEncoder` | `json(bytes(sys.inputs.context))` | Dictionary |
| `YamlContextEncoder` | `yaml(bytes(sys.inputs.context))` | Dictionary |
| `CsvContextEncoder` | `csv(bytes(sys.inputs.context))` | List of uniform, flat mappings |

All built-in encoders support the following context value types. CSV supports the
scalar entries only because each value occupies one table cell.

- `str`
- `int`
- `float`
- `datetime.datetime`, `.time`, and `.date`
- `list`
- `dict`

`decimal.Decimal` and `uuid.UUID` are also supported and are represented as strings.
TOML preserves native date and time values. JSON, YAML, and CSV serialize dates,
times, and datetimes as ISO 8601 strings.

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

To use context within a Typst template, parse the incoming data with the function
for the selected encoder. For example, a TOML template begins with:

```typst
#let ctx = toml(bytes(sys.inputs.context))
```

This assigns the parsed context to the Typst variable `ctx`, which can then be used
in the template like any other variable. For example, if your context was
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

## Extending context encoders

Register custom value encoders on an encoder instance to support application-specific
types. See the [context encoder reference][context-encoders] for the interface and
registration example. The registration belongs to that instance, so use the same
instance configured by `CONTEXT_ENCODER`.

CSV contexts must be a list of mappings with identical string field names. Nested
dictionaries and lists can't be placed in CSV cells.

<!-- Links -->

[context-encoders]: ../reference/context-encoders.md
[tinymist]: https://github.com/Myriad-Dreamin/tinymist
