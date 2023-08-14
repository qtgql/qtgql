## Schema and operation reasoning - (concrete and proxy Schema) 
Each operation in qtgql would generate a "proxy schema" that include only the used types
in this operation and only the used fields in those types.

## Cross-operation updates - (Root types are "singletons")
If operation X fetched some data and operation Y is also relying on this data (or a fraction of it)
it would be ideal that they would be able to update each other.  

To achieve this the `Mutation` /  `Subscription` / `Query` types are singletons-ish.
They exist for as long as one operation is using them otherwise they are deleted and once
an operation is instantiated a new instance would get created.

## Memoized fields - (Basic caching)
- Concrete fields are cached on the concrete instances.
- The concrete field type doesn't always (actually mostly doesn't) matches it's proxied type.
- Concrete fields that have arguments are cached by arguments to avoid unwanted updates
check [](../server-requirements.md#pure-fields) for more  details.

## Garbage collection
TBD

## Node Interface
TBD

## Implementation details
The codegen would generate `<OperationName>.cpp/hpp` for each operation defined in
`operaitons.graphql`.  

Every operation is entitled to:  

- Deserialize and update (if needed) **concrete** types based on the specific fields was queried.
- Deserialize and update (if needed) **proxy** types based on the specific fields was queried.
- Connect to signals from the concrete instances to the proxied instances and update the proxied  and emit 
signals when needed.
