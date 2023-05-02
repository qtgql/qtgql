
# Create Your own custom scalar
Although **QtGQL** provides some [frequently used scalars](./custom_scalars.md), you might have your own complex scalars.

## Tutorial - Country scalar
In order to deserialize a scalar for it to be compatible with Qt we created
`BaseCustomScalar`. For example if you have a scalar of country code, you want to show the user a readable value.

Here is a simple implementation

```python
from __future__ import annotations
from qtgqlcodegen.py.runtime.custom_scalars import BaseCustomScalar
from typing import Optional

country_map = {
    'isr': 'israel'
}

# BaseCustomScalar[<typeof default_value>, <typeof graphql_value>]
class CountryCode(BaseCustomScalar[str, str]):
    GRAPHQL_NAME = "CountryCode"
    DEFAULT_VALUE = "israel"  # this would be the default value.

    def parse_value(self) -> str:
        return self._value  # used in operation variables.

    @classmethod
    def deserialize(cls, v: Optional[str] = None) -> CountryCode:
        if v:
            return cls(country_map[v])
        return cls()

    def to_qt(self) -> str:
        return self._value


assert CountryCode.deserialize('isr').to_qt() == 'israel' == CountryCode().to_qt()
```
    !!! Note
        You would need to add this in your config
    ```python
    # config.py
    from qtgqlcodegen.py.compiler.config import QtGqlConfig


    QtGqlConfig(custom_scalars={CountryCode.GRAPHQL_NAME: CountryCode}, ...)
    ```

## API

::: qtgql.py.runtime.custom_scalars
