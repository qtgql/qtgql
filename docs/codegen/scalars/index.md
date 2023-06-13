# Scalars

The GraphQL specification includes default scalar types Int, Float, String, Boolean, and ID. Although these scalars cover the majority of use cases, some applications need to support other atomic data types (such as Date) or add validation to an existing type. To enable this, you can define custom scalar types.

## 'Builtins' scalars
These scalars are represented by "primitive" type and not by our scalar proxy.

- `String`, maps to `QString`
- `Int`, a signed 32-bit integer, maps to `int`
- `Float`, a signed double-precision floating-point value, maps to `f<number>`
- `Boolean`, true or false, maps to  `bool`
- `ID`, a specialised `String` for representing unique object identifiers, maps to `QString`
- `UUID`, maps to `QUuid`
- `Void`, `nullptr`.
