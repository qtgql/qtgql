Release type: minor

This release removes the previous approach of using `fetch` and `refetch`.

Instead, the user would call `execute()` on the operation handler.
It is important to note that every time you call `set_variables` on the operation handler,
the network layers will ignore the previous execution.

#### Bug Fixes:
- Bad HTTP responses will now call the `on_error` callback and can be handled ny
the operation handler just as if it was an operation error. Previously, failed HTTP responses
would cause the operation handler to be in a stale state, and it couldn't be used again.
- errors were not piped down to qml proxy handler. Now they are.
