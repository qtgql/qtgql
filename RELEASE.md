Release type: minor

### Features
- Support "non-node" objects on lists.

### Refactor
- When updating a proxy object field, instead of deleting it and creating a new one,
replace it with the new concrete and emit only the signals that are needed.

### Bug fixed
- Arguments not supported on scalar types.
