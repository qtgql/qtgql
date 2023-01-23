from PySide6.QtCore import Property, QObject, Signal
from qtgql.itemsystem import GenericModel, role
from qtgql.itemsystem.schema import Schema
from qtgql.itemsystem.type_ import get_base_type

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

    pChanged = Signal()

    def set_prop(self, v: str):
        self._private_prop = v
        self.pChanged.emit()

    @Property(type=str, notify=pChanged, fset=set_prop)
    def prop(self) -> str:
        return self._private_prop


schema = Schema(query=Apple)
