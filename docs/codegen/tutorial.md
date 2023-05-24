## Installation


First install the python codegen package.
!!! Note
    this package is used for the codegen and
    will not be needed in production.

<div class="termy">

```console

// It is MOST RECOMMENDED to use virtual-environment...

$ pip install qtgql

---> 100%
```
</div>

Now you'll need to link against qtgql target
(TBD)



## Setup
Set up a `graphql` dir inside it create a file named `schema.graphql` (dump your schema SDL there)
and another file named `operations.graphql` and declare the queries / subscriptions / mutations you want to use there.

Create a Python script named `qtgqlconfig.py`
!!! Warning
    This (`qtgqlconfig.py`) name is obliged.

Point your config to that directory
```python
from qtgqlcodegen.config import QtGqlConfig
from pathlib import Path

myconfig = QtGqlConfig(graphql_dir= Path(__file__).parent / '.graphql')
```
Now in your `pyproject.toml` add the full import path
for `myconfig`:

```yaml
[ tool.qtgql ]
config = "myapp.config:myconfig"
```
Now we will generate code based on the graphql operations defined in `graphql/operations.graphql`

<div class="termy">

```console

// Make sure that your virtual-env is active

$ qtgql gen

---> 100%
```

</div>

Now you project structure should look like this (with the generated files)

```bash
├── graphql
│   ├── __generated__
│   │   ├── CMakeLists.txt
│   │   ├── MainQuery.cpp
│   │   ├── MainQuery.hpp
│   │   └── schema.hpp
│   ├── operations.graphql
│   └── schema.graphql
├── __pycache__
│   └── qtgqlconfig.cpython-311.pyc
├── qtgqlconfig.py
└── test_scalarstestcase.cpp
```

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
| GraphQL type                                                | Default                                             |
|-------------------------------------------------------------|-----------------------------------------------------|
| `Int`                                                       | `qtgql::DEFAULTS::INT` *(compiler lowest int)*      |
| `String`                                                    | `" - "`                                             |
| `Float`                                                     | `qtgql::DEFAULTS::FLOAT` *(compiler lowest double)* |
| `ID`                                                        | `'9b2a0828-880d-4023-9909-de067984523c'`            |
| `Boolean`                                                   | `false`                                             |
| `UUID`                                                      | `QUuid("9b2a0828-880d-4023-9909-de067984523c")`     |
| `List` or in our context a `QAbstractListModel`             | `<modelname>` Blank corresponding generated model   |
| `ObjectType` or in our context an `QObject` with properties | `None`                                              |
| `SCALAR`                                                    | Provided by scalar implementation.                  |


## Usage

### Handling operation errors
(TBD)
