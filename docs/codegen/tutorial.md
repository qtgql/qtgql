# Graphql Codegen

## Intro

TBD

## Setup
Somewhere on your application (probably in config.py)
add our codegen configurations.
```python
# myapp/config.py
from qtgql.codegen.py.config import QtGqlConfig
from pathlib import Path

myconfig = QtGqlConfig(url="http://localhost:8000/graphql",
                       output=Path.cwd().parent / '__generated.py'
                       )
```
Now in your `pyproject.toml` add the full import path
for `myconfig`:

```yaml
[ tool.qtgql ]
config = "myapp.config:myconfig"
```
Now `qtgql` knows how to query your server for
introspection data, you just need to call

<div class="termy">

```console

// Make sure the server is on 😉

$ poetry run qtgql gen

---> 100%
```

</div>

And your typed are generated...

## Note about optionals
This library will try to set default values for fields if they were not fetched by the query
or to be used by `QGraphQListModel.currentObject`,
This reduces unexpected bugs significantly.

!!! Note
    Object types are currently optional because two types
    can refer each-other and cause recursion error, see [#84](https://github.com/nrbnlulu/qtgql/issues/84)

```qml
Item{
    property int size: object?.size
}
```
If `object` would be null property assignment would fail since
you can't assign `undefined` to `int`.

Therefore, **every generated type** has a default value,
including scalars and custom-scalars.
### Defaults mapping
| GraphQL type                                                | Default                                           |
|-------------------------------------------------------------|---------------------------------------------------|
| `Int`                                                       | `0`                                               |
| `String`                                                    | `" - "`                                           |
| `Float`                                                     | `0.0`                                             |
| `ID`                                                        | `'9b2a0828-880d-4023-9909-de067984523c'`          |
| `Boolean`                                                   | `False`                                           |
| `UUID`                                                      | `'9b2a0828-880d-4023-9909-de067984523c'`          |
| `List` or in our context a `QAbstractListModel`             | `<modelname>` Blank corresponding generated model |
| `ObjectType` or in our context an `QObject` with properties | `None`                                            |
| `SCALAR`                                                    | Provided by scalar implementation.                |


## Usage

(TBD)
