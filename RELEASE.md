Release type: minor

Initial support for unions.
currently unions are represented as a `QObject*`
and user would need to cast it based on the type name.

TODO:
- [ ] Create a base class for proxy objects with `__typename` property
