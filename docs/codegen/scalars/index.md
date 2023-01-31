# Scalars

The GraphQL specification includes default scalar types Int, Float, String, Boolean, and ID. Although these scalars cover the majority of use cases, some applications need to support other atomic data types (such as Date) or add validation to an existing type. To enable this, you can define custom scalar types.

## Builtin scalars
These scalars are represented by a Python "builtin" type, These are basically "no-op"
scalars since we won't modify the value came from the `json` response.

- `String`, maps to Python’s `str`
- `Int`, a signed 32-bit integer, maps to Python’s `int`
- `Float`, a signed double-precision floating-point value, maps to Python’s `float`
- `Boolean`, true or false, maps to Python’s `bool`
- `ID`, a specialised `String` for representing unique object identifiers
- `UUID`, maps to Python’s `str`

!!! Note "UUID"
    Although you could expect of UUID to map to [Python's UUID](https://docs.python.org/3/library/uuid.html#uuid.UUID)
    Since it would come with performance penalty and the advantages are nominal, we decided to stick with a no-op scalar.

[//]: # (# TODO: add note about uuid)
