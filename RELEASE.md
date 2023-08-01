Release type: minor

This release adds support for list of scalars.

### Breaking Changes

- Models now expose `data` role instead of `qtObject` role since
it can also be an `int` for example.
