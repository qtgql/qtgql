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
    we are using a glob to find it.

Point your config to that directory
```python
from qtgqlcodegen.config import QtGqlConfig
from pathlib import Path

myconfig = QtGqlConfig(graphql_dir= Path(__file__).parent / '.graphql')
```

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
├── qtgqlconfig.py
└── test_scalarstestcase.cpp
```


## Usage

### Handling operation errors
(TBD)
