CHANGELOG
=========

0.111.0 - 2023-03-06
--------------------

This release adds support for list of unions.

**This release also deprecates default object on QGraphQListModel**

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #125](https://github.com/nrbnlulu/qtgql/pull/125/)


0.110.1 - 2023-03-02
--------------------

This release adds support for types without `ID!` field.
fixes [#115](https://github.com/nrbnlulu/qtgql/issues/115)

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #116](https://github.com/nrbnlulu/qtgql/pull/116/)


0.110.0 - 2023-03-01
--------------------

This release adds support for updates.
It does this by generating for each query handler
an object that represents the selections for this query.
Then if the data is being compared against local data as follows

1. __builtin scalars__ - compared against the current value.
2. __custom scalars__ - By default compared against the inner value of the custom scalar.
3. __object_type__ - will compare against each field (generated on `update()`),
 - Note: if the object had the same ID! then the fields setter should not be called since the updates only
  occur at the child level, thus avoiding unnecessary updates.
edge cased:
 - new id reached: resolution -> create a new object and replace the pointer with the field setter.
 - field was null before (ATM objecttypes are the only real fields that can be null): resolution -> use setter on this field
 -
4. __unions__ - if `__typename` is different will cause a whole update, else similar to (3)
5. __enums__ - compare against the enum value / name (which the same string).
6. __lists a.k.a models__ -- since lists just store a pointer (or a key in the store) to a node and the node itself
already compared when `.from_dict` called on the raw-node,
we should just compare if the pointers points the right index so first crop the length of the list
to the length of the arrived data, then for each index compare the `ID!` and replace correspondingly if ID matched
call `update()` on that node.



This release also introduce `typename` property on each object type.
This is used by unions deserializers and can be useful for rendering specific component
based on the typename.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #112](https://github.com/nrbnlulu/qtgql/pull/112/)


0.109.0 - 2023-02-22
--------------------

This release adds initial support for type-store.
The type store is the source of truth for a given type.
All CRUD operations will occur on store level.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #106](https://github.com/nrbnlulu/qtgql/pull/106/)


0.108.0 - 2023-02-20
--------------------

This release adds initial implementation for type-store,
each type would have a dedicated store, and it would be used to CRUD
the instances.

0.107.0 - 2023-02-20
--------------------

This release adds `UseQuery` instead of using just the singleton generated type.
```qml
import generated.<Environment name> 1.0 as G
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

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #104](https://github.com/nrbnlulu/qtgql/pull/104/)


0.106.2 - 2023-02-15
--------------------

This release adds support for custom network access
by implementing the `NetworkLayerProto` protocol.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #101](https://github.com/nrbnlulu/qtgql/pull/101/)


0.106.1 - 2023-02-15
--------------------

This release fixes [issue #96](https://github.com/nrbnlulu/qtgql/issues/96).

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #97](https://github.com/nrbnlulu/qtgql/pull/97/)


0.106.0 - 2023-02-14
--------------------

### This release adds QML query handlers generation.

i.e:

**File**: _main.qml_

```qml
import QtGql 1.0 as Gql

Item{
    // `MainQuery` is generated from the query we write here.
    // the name is based on the operationName (MainQuery)
    Gql.MainQuery{id: query
        graphql: `query MainQuery {...}`
    }
    Text{
        text: query.data.somefield
    }
}
```

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #89](https://github.com/nrbnlulu/qtgql/pull/89/)


0.105.4 - 2023-02-08
--------------------

This release fixes [#84](https://github.com/nrbnlulu/qtgql/issues/84).
By setting default value for object type to null.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #87](https://github.com/nrbnlulu/qtgql/pull/87/)


0.105.3 - 2023-02-08
--------------------

This release fixes [#84](https://github.com/nrbnlulu/qtgql/issues/84).
By setting default value for object type to null.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #85](https://github.com/nrbnlulu/qtgql/pull/85/)


0.105.2 - 2023-02-08
--------------------

This release drops generation of model for each type instead
it uses Generic to annotate the model inner type. resolves [#81](https://github.com/nrbnlulu/qtgql/issues/81)
Also, it adds a default currentObject.
resolves [#80](https://github.com/nrbnlulu/qtgql/issues/80)

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #82](https://github.com/nrbnlulu/qtgql/pull/82/)


0.105.1 - 2023-02-07
--------------------

This release generates in-place deserializers instead of calling
pre-defined functions.
See [issue #17](https://github.com/nrbnlulu/qtgql/issues/17) for more details.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #76](https://github.com/nrbnlulu/qtgql/pull/76/)


0.105.0 - 2023-02-07
--------------------

This release adds default values for every type in the `__init__` method.
Resolves [issue #39](https://github.com/nrbnlulu/qtgql/issues/39)

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #72](https://github.com/nrbnlulu/qtgql/pull/72/)


0.104.4 - 2023-02-06
--------------------

migrate slot to use types from typingref
This release fixes [issue #3](https://github.com/nrbnlulu/qtgql/issues/3)

Contributed by [xiangxw](https://github.com/xiangxw) via [PR #59](https://github.com/nrbnlulu/qtgql/pull/59/)


0.104.3 - 2023-02-05
--------------------

This release adds `currentObject` property for codegen BaseModel.
This is useful in QML where you have to access the current selected object outside
the delegate.
Fixes [#65](https://github.com/nrbnlulu/qtgql/issues/65)

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #66](https://github.com/nrbnlulu/qtgql/pull/66/)


0.104.2 - 2023-02-02
--------------------

This release fixes [issue #61](https://github.com/nrbnlulu/qtgql/issues/61)

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #62](https://github.com/nrbnlulu/qtgql/pull/62/)


0.104.1 - 2023-02-02
--------------------

This release fixes [issue #58](https://github.com/nrbnlulu/qtgql/issues/58)

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #60](https://github.com/nrbnlulu/qtgql/pull/60/)


0.104.0 - 2023-02-01
--------------------

This release adds basic support for graphql enums.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #57](https://github.com/nrbnlulu/qtgql/pull/57/)


0.103.0 - 2023-01-31
--------------------

This release adds support for strawberry builtin scalars
- Date - an ISO-8601 encoded [date](https://docs.python.org/3/library/datetime.html#date-objects)
- Time - an ISO-8601 encoded [time](https://docs.python.org/3/library/datetime.html#time-objects)
- Decimal- a [Decimal](https://docs.python.org/3/library/decimal.html#decimal.Decimal) value serialized as a string
- UUID -  a [UUID](https://docs.python.org/3/library/uuid.html#uuid.UUID) value serialized as a string

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #44](https://github.com/nrbnlulu/qtgql/pull/44/)
