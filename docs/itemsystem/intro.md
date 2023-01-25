# Introduction

In order to generate a `QAbstractListModel` with ease
you can use our "itemsystem" framework.

Say we want to show a model apples and apples might have worms
inside so there is a worm model as well.

Any class that extends `MyBaseType` would automatically
generate a QAbstractListModel with the proper roles in it.

```python
from __future__ import annotations
from PySide6.QtCore import QObject, Property, QCoreApplication
from qtgql.itemsystem import get_base_type, role, GenericModel, asdict

MyBaseType = get_base_type()
class Apple(MyBaseType):
    color: str = role()
    size: int = role()
    worms: GenericModel[Worm]
```

???+ note
    We haven't defined Worm yet, though `MyBaseType` can handle lazy
    definitions.


```python

class Worm(MyBaseType):
    name: str = role()
    color: str = role(default="green")

class MyApp(QObject):
    def __init__(self):
        super().__init__(None)
        data = asdict(Apple(color='red', size=12, worms=[asdict(Worm(name='steve')) for _ in range(5)]))
        self._apple_model: GenericModel[Apple] = Apple.Model(data=[data])

    # expose the model to QML:
    @Property(type=QObject, constant=True)
    def appleModel(self) -> GenricModel[Apple]:
        return self._apple_model

    def check_apple_color(self):
        # `color` is auto completed!
        assert self._apple_model._data[0].color == 'red'
        self.deleteLater()

app = MyApp()
assert app._apple_model is app.appleModel
app.check_apple_color()
```


::: itemsystem.core
