Release type: minor

This release adds `UseQuery` instead of using just the singleton generated type.
```qml
import Generated 1.0 as G
G.UseQuery{
    operationName: 'MainQuery'
    Text{
        text: G.MainQuery.completed? G.MainQuery.data: "loading..."
    }
}
```
This release also impose a new style for declaring operations.
User would need to provide a schema.graphql and operations.graphql
under the same directory and import the operation names from qml.
as per [#100](https://github.com/nrbnlulu/qtgql/issues/100)
