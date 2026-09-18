# 0001 Template Context Transfer

- Date: 2025-08-20
- Author: [Jonathan Moss][jmoss]
- Status: `Active`

## Context

To make a templating engine useful we need to be able to pass _context_ into it so that
the engine itself can interpolate the values into the template. Django's built-in class
based views provide mechanisms to build out this context as an arbitrarily shaped dict.

Typst isn't just another Python package, it's a compiled Rust library. So we can't
simply pass the dictionary across. We need to make use of Typst's own method of
providing data - `sys_inputs`. For the Typst CLI this is an optional command switch to
which you can pass `key=value` pairs.

We could do a one to one map - each key in the Django context is mapped to its own
`sys_input` key. However, the Django context dict can contain any type of value,
including embedded dicts or lists.

There are 2 ways we could accommodate this:

1. Disallow any complex types within the context. Limit it to simple scalar types like
    string and integers.
1. Make use of some kind of serialization that Typst can understand to send through more
    complex data.

Typst itself supports a number of different serialization formats:

- CBOR: Concise Binary Object Representation
- CSV: Character Separated Values
- JSON: JavaScript Object Notation
- TOML: Tom's Obvious Minimal Language
- XML: eXtensible Markup Language
- YAML: Yet Another Markup Language

Python has built in support for CSV and JSON encoding as well as XML. XML might be a
good choice as it's flexible but it doesn't have a huge number of data types out the
box. So more work would be needed in the Typst template itself parse the data into the
formats needed.

CSV files are table of data but don't really define any data types meaning the typst
template would again need to parse the data into the correct types.

JSON is the _de-facto_ standard for web api but it also has a limited set of types
supported. For example, it doesn't have support for dates and datetimes. So these tend
to be converted to strings - requiring to consumer to parse them back into their correct
types. YAML is a super-set of JSON, it does support a greater range of types.

Only reading TOML is supported out the box with Python. Writing requires an additional
library. It has a similar range of built-in type as JSON, but with the notable addition
of dates and time - with optional offsets.

CBOR is again built on a compatibility with JSON but in a space efficient binary format.
The support in Typst requires either the raw bytes or a path to a file containing those
bites. For this reason I am discounting it as I am not sure that we can safely pass raw
bytes across without the use of an intermediate file.

If we're already serializing the context - we might as well pass it as a single well
known `sys_inputs` key value.

## Decision

We will initially use TOML encoded context data passed as a single value to `sys_inputs`
under the name `context`.

The TOML serializer will be augmented with some basic functionality for encoding common
types that aren't natively supported by TOML such as `Decimal`, `UUID` and to some
extent the `http.Request` object. We will also provide details on how one can extend
this further as needed.

To be honest, YAML was mostly rejected because I just don't like it as a serialization
format. I find it hard to mentally parse… which I will admit is a bit weird coming from
a Python Developer.

## Implications

The use of TOML provides support for the majority of standard data types, with
augmentation for others being added to the serializer to provide a slightly increased
range. That said, it's still limited. So we should provide details on how to extend it.

A future extension here would be to make the serialization itself pluggable. So should a
user prefer JSON or YAML.

<!-- Links -->

<!-- Abbreviations -->

*[ADR]: Architectural Decisions Record

[jmoss]: mailto:xirisr@gmail.com
