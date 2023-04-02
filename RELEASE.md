Release type: minor

This release adds support for interfaces as field types.
The property type would be of an interface
and all the types that implement that interface
would extend it.

Note that querying an interface automatically adds `__typename` in the fragment.
