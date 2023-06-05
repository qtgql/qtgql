Release type: patch

This release adds initial support for scalars. Querying a scalar is not yes feasible
though concrete objects are now uses correct inheritance hierarchy.

From this release onwards only types that comply with [`Node`](https://graphql.org/learn/global-object-identification) interface
would be treated as cache-able or update-able.
