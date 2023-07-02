CHANGELOG
=========

0.123.0 - 2023-07-02
--------------------

Initial support for interfaces.
Currently only interfaces there is no support for
node interfaces.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #294](https://github.com/qtgql/qtgql/pull/294/)


0.122.0 - 2023-06-27
--------------------

This release adds support for input types as operation variables.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #292](https://github.com/qtgql/qtgql/pull/292/)


0.121.1 - 2023-06-27
--------------------

This release adds support for enums updates and enums as operation variables.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #291](https://github.com/qtgql/qtgql/pull/291/)


0.121.0 - 2023-06-27
--------------------

This release adds support for update&deserialize types that
does not implement `Node` interface.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #289](https://github.com/qtgql/qtgql/pull/289/)


0.120.3 - 2023-06-26
--------------------

This release fixed an edge case where nested object would not update the nested object
if the nested object itself has changed.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #288](https://github.com/qtgql/qtgql/pull/288/)


0.120.2 - 2023-06-26
--------------------

This release adds support for updates of list of nodes.

When operation X queries for list of nodes, the list would
get deserialized and each proxy that contains that list would update it's model based on the new data.
if the node itself has changed the changed fields would emit their own signals
to indicate the UI for updates.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #284](https://github.com/qtgql/qtgql/pull/284/)


0.120.1 - 2023-06-25
--------------------

Migrate to "singleton" root types.
The advantage for this architecture is that the ui won't be updated every-time
a (next) message arrives, as well as for cross-operation updates.

To demonstrate the purpose of this specification image that
operation X queried for
```graphql
me{
    name
    profilePic
}
```

And after a while operation Y queried for:
```graphql
me{
    nickName
    profilePic
}
```
Assuming that the profile picture has changed, operation X **would be updated**
as well.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #282](https://github.com/qtgql/qtgql/pull/282/)


0.120.0 - 2023-06-21
--------------------

### Refactor
- Due to complexity issues deserializers and updaters are moved to operations scope.
Each operation will generate its own deserializers chain.
- Refactor operation evaluation, uses similar technique that used by schema evaluations.
Much more readable.
- Move root field out of the operation handler, instead create root types as well.

### Features
- Cache by arguments see #254

### CD
- refactor bot comment
- add no todos check

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #271](https://github.com/qtgql/qtgql/pull/271/)


0.119.13 - 2023-06-13
---------------------

This release removes the previose `loose()` approach mainly due to complexity reasons.
Starting from now we have a periodic garbage collector on all `Node` derived classes.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #253](https://github.com/qtgql/qtgql/pull/253/)


0.119.12 - 2023-06-11
---------------------

This release adds support for optional nested objects
updates and gc.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #252](https://github.com/qtgql/qtgql/pull/252/)


0.119.11 - 2023-06-08
---------------------

This release adds support for updates & garbage collection of nested object types.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #250](https://github.com/qtgql/qtgql/pull/250/)


0.119.10 - 2023-06-08
---------------------

This release refactored the project structure and
added initial conan support.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #248](https://github.com/qtgql/qtgql/pull/248/)


0.119.9 - 2023-06-06
--------------------

This release adds support for using custom scalars (including ours) in
operation variables and also adds the update&gc tests for custom scalars.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #244](https://github.com/qtgql/qtgql/pull/244/)


0.119.8 - 2023-06-05
--------------------

This release migrates operations to not use a constant operation ID
as discussed in #230.

0.119.7 - 2023-06-05
--------------------

This release adds initial support for interfaces. Querying a interface is not yes feasible
though concrete objects are now uses correct inheritance hierarchy.

From this release onwards only types that comply with [`Node`](https://graphql.org/learn/global-object-identification) interface
would be treated as cache-able or update-able.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #239](https://github.com/qtgql/qtgql/pull/239/)


0.119.6 - 2023-06-04
--------------------

This release sets the first milestones for updates and garbage collection.
The initial PR was for OperationVariables testcase though it was too advanced at this point of the project
because it relied on advanced updated so I first started with scalars and decided to narrow the context of the PR.

The original PR branch is kept as a reference at #232

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #237](https://github.com/qtgql/qtgql/pull/237/)


0.119.5 - 2023-05-31
--------------------

This release adds support for GraphQL enums.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #229](https://github.com/qtgql/qtgql/pull/229/)


0.119.4 - 2023-05-30
--------------------

Add support list of objects.
When a list is deserialized the instances are mapped based on operation ID
since lists are not part of the [field stability](https://graphql.org/learn/global-object-identification/#field-stability) spec.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #225](https://github.com/qtgql/qtgql/pull/225/)


0.119.3 - 2023-05-28
--------------------

Adding support for optional object inside an object.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #224](https://github.com/qtgql/qtgql/pull/224/)


0.119.2 - 2023-05-28
--------------------

This release adds support for nested object types.
operation proxies does not refer to the concrete instance directly
rather they are pointing to an instantiated
proxy of the concrete.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #222](https://github.com/qtgql/qtgql/pull/222/)


0.119.1 - 2023-05-24
--------------------

This release moves qtgql subcomponents into namespaces.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #221](https://github.com/qtgql/qtgql/pull/221/)


0.119.0 - 2023-05-24
--------------------

This release adds support for optional (nullable) scalars.

and initial support for setting variables.
i.e for this query:
```graphql
query MainQuery($returnNone: Boolean! = false) {
  user(retNone: $returnNone) {
    name
    age
    agePoint
    uuid
    birth
  }
}
```

You could set `$returnNone` to `true` like this.

```cpp
auto mq = std::make_shared<mainquery::MainQuery>();
mq->setVariables({true});
mq->fetch();
```

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #219](https://github.com/qtgql/qtgql/pull/219/)


0.118.0 - 2023-05-23
--------------------

This release adds support for custom scalars.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #211](https://github.com/qtgql/qtgql/pull/211/)


0.117.0 - 2023-05-22
--------------------

This release is the initial migration step to C++.

a lot have changed and currently almost nothing is supported.
You can keep yourself uptodate for when we reach a stable release.

*Windows compilation is not working yet.*

Initial pr was #197
![architecture](https://user-images.githubusercontent.com/88795475/239720860-120297b0-c7b7-45b1-bbb5-8e02af806aaa.png)

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #210](https://github.com/qtgql/qtgql/pull/210/)


0.116.1 - 2023-04-04
--------------------

This release improves performance of `GqlTypeHinter` by caching
evaluation of attributes.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #185](https://github.com/qtgql/qtgql/pull/185/)


0.116.0 - 2023-04-02
--------------------

This release adds support for interfaces as field types.
The property type would be of an interface
and all the types that implement that interface
would extend it.

Note that querying an interface automatically adds `__typename` in the fragment.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #180](https://github.com/qtgql/qtgql/pull/180/)


0.115.1 - 2023-03-29
--------------------

This release migrates to use [typingref](https://github.com/nrbnlulu/typingref) for type annotations introspection.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #174](https://github.com/nrbnlulu/qtgql/pull/174/)


0.115.0 - 2023-03-26
--------------------

This release adds initial support for subscriptions.

_Also fixing [#157](https://github.com/nrbnlulu/qtgql/issues/157) because it was a two lines diff fix._

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #167](https://github.com/nrbnlulu/qtgql/pull/167/)


0.114.0 - 2023-03-26
--------------------

This release adds initial subscription support.

0.113.4 - 2023-03-26
--------------------

fix mypy plugin.

I couldn't fix mypy for itemsystem `get_base_type()` ATM.

0.113.3 - 2023-03-23
--------------------

This release fixes a bug that `completed` and `operationOnFlight` wouldn't be updated
correctly.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #164](https://github.com/nrbnlulu/qtgql/pull/164/)


0.113.2 - 2023-03-22
--------------------

This release adds support for operation errors hooks.
i.e
```python
from qtgqlcodegen.py.runtime.queryhandler import BaseOperationHandler
from qtgqlcodegen.tools import slot

from PySide6.QtCore import QObject

class Foo(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        operation: BaseOperationHandler
        operation.error.connect(self.on_error)

    @slot
    def on_error(self, err: list[dict]) -> None:
        print(err)
```

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #162](https://github.com/nrbnlulu/qtgql/pull/162/)


0.113.1 - 2023-03-22
--------------------

This release fixes an edge case where root types with no id fields
would cause errors on updates.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #160](https://github.com/nrbnlulu/qtgql/pull/160/)


0.113.0 - 2023-03-22
--------------------

This release adds initial support for mutations.

- [x] Mutation handler (on par with query handler).
- [x] commit slot. - on par with `refetch()` / `fetch()`
- [x] Support variables
Every operation would generate <OperationName>Variables type, this type would be the property
The commit slot would have the types arguments on it, and for every type is not a plain JS type
we would generate a factory slot (accessible from QML), those types would be transformed to dictionaries and further on to JSON.

  - [x] scalars
  - [x] CustomScalars
  - [x] objectTypes
- [x] Should have a `property` for `operationOnFlight` (maybe queries as well)

- [x] Test usage from QML Already covered by query tests, all operations use the same base class.
- [ ] <s>Update docs.</s> Would update in a separate PR when updating major version.
- [x] if there are variables for an operation than it shouldn't auto fetch itself (when used in QML)
we should provide something like `property bool autofetch: false`

### Notes:
- This release also made `BaseQueryHandler` not a singleton, because you could have different
filters (on different handlers). Instead of `UseQuery{operationName: '...'}`
- There would be `Consume<operationName>{}` QQuickItem that would internally use
the generated <operationName> handler. By using this Item you declare that as long as this component lives
the data it retains wouldn't be gc'eed.
- This release changed the data property on operation handlers to handlerData.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #147](https://github.com/nrbnlulu/qtgql/pull/147/)


0.112.1 - 2023-03-12
--------------------

This release adds support for queries refetching.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #143](https://github.com/nrbnlulu/qtgql/pull/143/)


0.112.0 - 2023-03-12
--------------------

This release adds initial support for garbage collection in order to avoid
caching too many objects.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #137](https://github.com/nrbnlulu/qtgql/pull/137/)


0.111.4 - 2023-03-09
--------------------

This release updates dependencies.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #136](https://github.com/nrbnlulu/qtgql/pull/136/)


0.111.3 - 2023-03-08
--------------------

This release adds support for `QGraphQListModel.clear()`.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #133](https://github.com/nrbnlulu/qtgql/pull/133/)


0.111.2 - 2023-03-08
--------------------

This release adds minimal support for future annotations in slots or other parts
of the lib that uses TypeHinter.

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #132](https://github.com/nrbnlulu/qtgql/pull/132/)


0.111.1 - 2023-03-06
--------------------

This release fixes a bug that inner model class would get overridden
by ItemBase metaclass.
```python
class StatusIndicator(ItemBaseType):
    class Model(GenericModel):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
```

Contributed by [ניר](https://github.com/nrbnlulu) via [PR #128](https://github.com/nrbnlulu/qtgql/pull/128/)


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
