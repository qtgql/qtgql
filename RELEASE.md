Release type: minor

This release adds support for recursive input objects.

### BREAKING CHANGES:
- From now on, input objects are heap allocated.
This is due to this specific use case that input objects might reference themselves.
