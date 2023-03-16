Release type: minor

This release adds initial support for mutations.

- [ ] Mutation handler (on par with query handler).
- [ ] commit slot. - on par with `refetch()` / `fetch()`
- [ ] Support variables
Every operation would generate <OperationName>Variables type, this type would be the property
The commit slot would have the types arguments on it, and for every type is not a plain JS type
we would generate a factory slot (accessible from QML), those types would be transformed to dictionaries and further on to JSON.

  - [x] scalars
  - [ ] CustomScalars
  - [x] objectTypes
- [x] Should have a `property` for `operationOnFlight` (maybe queries as well)
- [ ] Mutations (or subscriptions) that return an iterable can accept an id for that iterator (to update it) (currently `QGraphQLListModel`)
and when the data arrives it would update it.
- [ ] Test usage from QML
- [ ] Should support some kind of updater hook.
- [ ] Update docs.
- [ ] if there are variables for an operation than it shouldn't auto fetch itself (when used in QML)
we should provide something like `property bool autofetch: false`

### Notes:
- This release also made `BaseQueryHandler` not a singleton, because you could have different
filters (on different handlers). Instead of `UseQuery{operationName: '...'}`
- There would be `Require<operationName>{}` QQuickItem that would internally use
the generated <operationName> handler. By using this Item you declare that as long as this component lives
the data it retains wouldn't be gc'eed.
