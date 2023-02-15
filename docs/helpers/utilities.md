## Utilities
general helpers for ease of development.

### slot
Creates a [slot](https://doc.qt.io/qt-6/signalsandslots.html) out of type annotation.

```python
from qtgql.tools import slot
from PySide6.QtCore import QObject


class Foo(QObject):
    def __init__(self):
        super().__init__(None)
        self.data: str = 'foo'

    @slot
    def set_data_from_qml(self, text: str) -> None:
        """
        This is reachable from QML!
        """
        self.data = text


foo = Foo()
foo.set_data_from_qml('bar')
assert foo.data == 'bar'
```
::: tools.slot.slot

### Auto-property
Create [Properties](https://doc.qt.io/qt-6/qproperty.html) with a dataclass syntax

Example:
```python
from qtgql.tools import define_properties

@define_properties
class Apple:
    color: str
    size: int

apple = Apple(color="red", size=92)
apple_as_qt: Apple = apple.properties
assert apple_as_qt.color == apple.color
apple.color = "green"
assert apple_as_qt.color == "green"
```

::: tools.autoproperty.define_properties
