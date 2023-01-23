from PySide6.QtCore import Property, QObject, QTimer, Signal
from qtgql import slot
from qtgql.itemsystem import GenericModel, role
from qtgql.itemsystem.schema import Schema
from qtgql.itemsystem.type_ import get_base_type

from tests.conftest import fake

schema = get_base_type()


class Worm(schema):
    name: str = role()
    family: str = role()
    size: int = role()


class Apple(schema):
    size: int = role()
    owner: str = role()
    color: str = role()
    worms: GenericModel[Worm] = role(default=None)
    p_class: QObject = role(factory=lambda: PropertyClass())


# POC that you can pass object with properties from QAbstractListModel:
class PropertyClass(QObject):
    def __init__(self):
        super().__init__(None)
        self._private_prop = "Hellewww"
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.replace_prop_val)
        self.timer.start()

    pChanged = Signal()

    @slot
    def replace_prop_val(self) -> None:
        self.set_prop(fake.name())

    def set_prop(self, v: str):
        self._private_prop = v
        self.pChanged.emit()

    @Property(type=str, notify=pChanged, fset=set_prop)
    def prop(self) -> str:
        return self._private_prop


schema = Schema(query=Apple)
