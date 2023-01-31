# Scalars

The GraphQL specification includes default scalar types Int, Float, String, Boolean, and ID. Although these scalars cover the majority of use cases, some applications need to support other atomic data types (such as Date) or add validation to an existing type. To enable this, you can define custom scalar types.

## Builtin scalars
These scalars are represented by a Python "builtin" type

- `String`, maps to Python’s `str`
- `Int`, a signed 32-bit integer, maps to Python’s `int`
- `Float`, a signed double-precision floating-point value, maps to Python’s `float`
- `Boolean`, true or false, maps to Python’s `bool`
- `ID`, a specialised `String` for representing unique object identifiers

[//]: # (# TODO: add note about uuid)
