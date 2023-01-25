# qtgql
## Qt framework for building graphql driven QML applications
![PyPI - Downloads](https://img.shields.io/pypi/dm/qtgql)
![PyPI - Downloads](https://img.shields.io/pypi/dm/qtgql?style=for-the-badge)
![PyPI](https://img.shields.io/pypi/v/qtgql?style=for-the-badge)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/nrbnlulu/qtgql/tests.yml?label=tests&style=for-the-badge)

### Disclaimer
This project is currently under development and **it is not** production ready,
You can play-around and tell us what is wrong / missing / awesome :smile:.
### Intro
Qt-QML IMO is a big game changer
- you get native performance
- UI code is very clear and declarative
- Easy to customize
- Easy to learn

One of the big disadvantages in Qt-QML is that Qt-C++ API is very repititive and hard to maintain
for data-driven applications.

although it is tempting to just use `relay` or other `JS` graphql lib
there is a point where you would suffer from performance issues (:roll_eyes:  react-native).

### Solutions I had so far
To overcome Qt's "great" API I wrote [qtgql](https://github.com/nrbnlulu/qtgql) Initially it was just meant for API hacks
i.e
```py
# instead of
@Slot(argumeants=(str, int, str), result=str)
def some_slot(self, a, b, c):
    return "foo"

# gets return type from annotations
from qtgql import slot

@slot
def some_slot(self, a: str, b: int, c: list[str]) -> str:
    return "foo"
```

Also I have made generic models so that you won't have to define `roles` `data` `update` manage signals emission and
so much boilerplate code yourself.

you would just declare your model like this
```py
from qtgql.itemsystem.schema import Schema
from qtgql.itemsystem import role, GenericModel, get_base_type
BaseType = get_base_type()
class Worm(BaseType):
    name: str = role()
    family: str = role()
    size: int = role()


class Apple(BaseType):
    size: int = role()
    owner: str = role()
    color: str = role()
    worms: GenericModel[Worm] = role(default=None)



apple_model: GenericModel[Apple] = Apple.Model(schema=schema)
apple_model.initialize_data(data)  # dict with the correct fields
```


### GraphQL support
As I have proggresed with the codebase I realized that I can do better and possibly mimic some
features of graphql relay at the cost of making this project more opinionated.
So I decided to rename it to `qtgql` (previouslly cuter :cat: ).
Some of the current features:
 - Qt-native graphql-transport-ws network manager (supports subscriptions).
 - generic models that get created from dictionaries (with update, pop, insert implemeanted by default)
 - property classes that are accessible from QML, with dataclasses  syntax (using attrs)

### Future vision
- Code generation from schema inspection
Ideally every graphql type would be a `QObject` with `Property` for each field.
- possibly generate C++ bindings from schema inspection
- Query only what defined by the user (similar to how relay does this)
- Auto mutations
- Subscriptions



### Example Usage (no codegen):
The following example shows how qtgql can be used to query a graphql service.
*models.py*

```python
from qtgql.itemsystem import role, define_roles


@define_roles
class Worm:
    name: str = role()
    family: str = role()
    size: int = role()


@define_roles
class Apple:
    size: int = role()
    owner: str = role()
    color: str = role()
    # nested models are also supported!
    worms: Worm = role(default=None)
```
qtgql will create for you `QAbstractListModel` to be used in QML you only need to
define your models with `define_roles`.
qtgql initializes the data with a dict, in this case coming from graphql service.

*main.py*

```python
import glob
import os
import sys
from pathlib import Path

from qtpy.QtQml import QQmlApplicationEngine
from qtpy.QtCore import QObject, Signal
from qtpy import QtCore, QtGui, QtQml, QtQuick

from qtgql import slot
from qtgql.gqltransport.client import HandlerProto, GqlClientMessage, GqlWsTransportClient
from qtgql.itemsystem import GenericModel
from tests.test_sample_ui.models import Apple


class EntryPoint(QObject):
    class AppleHandler(HandlerProto):
        message = GqlClientMessage.from_query(
            """
            query MyQuery {
              apples {
                color
                owner
                size
                worms {
                  family
                  name
                  size
                }
              }
            }
            """
        )

        def __init__(self, app: 'EntryPoint'):
            self.app = app

        def on_data(self, message: dict) -> None:
            self.app.apple_model.initialize_data(message['apples'])

        def on_error(self, message: dict) -> None:
            print(message)

        def on_completed(self, message: dict) -> None:
            print(message)

    def __init__(self, parent=None):
        super().__init__(parent)
        main_qml = Path(__file__).parent / 'qml' / 'main.qml'
        QtGui.QFontDatabase.addApplicationFont(str(main_qml.parent / 'materialdesignicons-webfont.ttf'))
        self.qml_engine = QQmlApplicationEngine()
        self.gql_client = GqlWsTransportClient(url='ws://localhost:8080/graphql')
        self.apple_query_handler = self.AppleHandler(self)
        self.gql_client.query(self.apple_query_handler)
        self.apple_model: GenericModel[Apple] = Apple.Model()
        QtQml.qmlRegisterSingletonInstance(EntryPoint, "com.props", 1, 0, "EntryPoint", self)  # type: ignore
        # for some reason the app won't initialize without this event processing here.
        QtCore.QEventLoop().processEvents(QtCore.QEventLoop.ProcessEventsFlag.AllEvents, 1000)
        self.qml_engine.load(str(main_qml.resolve()))

    @QtCore.Property(QtCore.QObject, constant=True)
    def appleModel(self) -> GenericModel[Apple]:
        return self.apple_model


def main():
    app = QtGui.QGuiApplication(sys.argv)
    ep = EntryPoint()  # noqa: F841, this collected by the gc otherwise.
    ret = app.exec()
    sys.exit(ret)


if __name__ == "__main__":
    main()
```

![Example](assets/qtgql.gif)
