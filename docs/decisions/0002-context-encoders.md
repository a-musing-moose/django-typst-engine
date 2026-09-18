# 0002 Context Encoders

- Date: 2026-09-18
- Author: [Jonathan Moss][jmoss]
- Status: `Active`

## Context

[ADR 0001][context-adr] established TOML as the initial format for transferring a
Django template context to Typst. It also anticipated allowing the serialization
format to be selected in the future.

Typst can deserialize TOML, JSON, YAML, CSV, CBOR, and XML. Different projects
have different interoperability requirements, so the template engine should allow
an application to choose a context encoding format without changing its rendering
workflow.

Every supported encoder must accept the same common context types: `str`, `int`,
`float`, `Decimal`, `UUID`, `date`, `time`, `datetime`, `list`, and `dict`. It
must also be possible to register application-specific type conversions. These
registrations should belong to an encoder instance so that separate template
engines can use different conversions in the same process.

CSV represents rows and columns rather than an arbitrarily shaped document. It
can only support a tabular context. XML is deliberately not included because its
element and attribute model would require a library-specific schema for the
general context structure. The Typst Python binding only accepts string
`sys_inputs` values, so it can't pass the raw bytes required by CBOR without a
temporary-file transport and its associated lifecycle.

## Decision

Context serialization is provided by a `ContextEncoder` interface. Each encoder
serializes a Django context to the string passed to Typst as `sys.inputs.context`.

`TypstEngineConfig` selects the encoder with the `CONTEXT_ENCODER` option. The
option contains a dotted path to a no-argument encoder class, following Django's
configured class style. When it's omitted, the engine uses the TOML encoder to
preserve the behavior established by ADR 0001.

The initial supported encoders are TOML, JSON, YAML, and CSV. CSV accepts only a
list of uniform, flat mappings. TOML retains its native date and time values.
JSON, YAML, and CSV serialize `date`, `time`, and `datetime` as ISO 8601 strings.
All encoders serialize `Decimal` and `UUID` as strings. Each format's
documentation will show the corresponding Typst parser and any format-specific
limitations.

Encoders expose instance-level registration for custom conversions. Built-in
encoders reuse common conversions for `Decimal`, `UUID`, and Django
`HttpRequest` objects.

## Implications

Templates must use the Typst parsing function corresponding to their configured
encoder. Applications choosing JSON, YAML, or CSV must parse ISO 8601 temporal
strings in Typst when they need temporal operations.

Supporting an encoder requires format-specific tests as well as contract tests
for the shared interface and custom conversion registration. Documentation must
describe the selected encoder in Django settings and the matching Typst template
setup.

XML and CBOR remain unsupported. A future CBOR proposal would need to define a
safe temporary-file creation, hand-off, and cleanup lifecycle before it could be
adopted.

<!-- Links -->

[context-adr]: 0001-context.md
[jmoss]: mailto:xirisr@gmail.com
