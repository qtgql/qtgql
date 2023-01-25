# Graphql Codegen

## Intro

TBD

## Setup
Somewhere on your application (probably in main.py)
add our codegen configurations. 
```python
from qtgql.codegen.py.config import QtGqlConfig
from pathlib import Path

myconfig = QtGqlConfig(url="http://localhost:8000/graphql",
                       output=Path(__file__).parent / '__generated.py'
                       )
```
Now in your `pyproject.toml` add the full import path
for `myconfig`:

```yaml
[ tool.qtgql ]
config = "myapp.main:myconfig"
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

## Usage

TBD...


