Release type: minor

Initial support for unions.
currently unions are represented as a `ObjectType *`
and user would need to cast it based on the `__typeName()` property.
