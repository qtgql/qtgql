Release type: minor

This release adds datetime scalar support by allowing
custom scalars. users can now add their own scalars like this:

```python
from qtgql.codegen.py.scalars import BaseCustomScalar
from datetime import datetime

class MyDateTime(BaseCustomScalar[datetime]):
    def to_qt(self) -> str | None:
        if self._value:
            return self._value.strftime(' %D:%H:%M: ')
        return None
```
This should be added in QtGqlConfig like so

```python
from qtgql.codegen.py.config import QtGqlConfig
my_scalars = {
    'MyDateTime': MyDateTime  # the key is a valid graphql name of the scalar
}

qtgqlconfig = QtGqlConfig(url=..., output=..., custom_scalars=my_scalars)
```
