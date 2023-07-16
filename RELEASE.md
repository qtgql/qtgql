Release type: minor

This release adds initial support for fragments.
- [x] Fragments on object types.
- [x] Fragments on interfaces.
- [x] Nested fragments
- [x] Fragments with variables usages.

Fragments are invisible user-wise. This means that they have no
runtime type, we are just unwrapping them in the operation evaluation phase.
