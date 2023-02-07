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
This library assumes that there is no such thing as optional datatypes,
This reduces unexpected bugs significantly.
For instance if in QML you are expecting that a type would have an inner type,
and you wanted to create a binding to that type you would need to have a custom
JS function on every property:
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
| datatype                                                    | Default                                         |
|-------------------------------------------------------------|-------------------------------------------------|
| `Int`                                                       | `0`                                             |
| `String`                                                    | `" - "`                                         |
| `Float`                                                     | `0.0`                                           |
| `ID`                                                        | `str()`                                         |
| `Boolean`                                                   | `False`                                         |
| `UUID`                                                      | `str()`                                         |
| `List` or in our context a `QAbstractListModel`             | `<modelname>` The corresponding generated model |
| `ObjectType` or in our context an `QObject` with properties | `<typename>` The corresponding generated object |


## Usage

(TBD)
