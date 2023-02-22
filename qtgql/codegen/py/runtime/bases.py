from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Generic, Optional, TypeVar

from PySide6.QtCore import QAbstractListModel, QByteArray, QObject, Qt, Signal

if TYPE_CHECKING:
    from typing_extensions import Self

from qtgql.tools import qproperty, slot

__all__ = ["QGraphQListModel", "get_base_graphql_object"]


class _BaseQGraphQLObject(QObject):
    type_map: dict[str, type[_BaseQGraphQLObject]]

    id: str
    __singleton__: Self
    __store__: ClassVar[QGraphQLObjectStore[Self]]

    def __init_subclass__(cls, **kwargs):
        cls.type_map[cls.__name__] = cls  # required to instantiate unions.
        cls.__store__ = QGraphQLObjectStore()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

    @classmethod
    def default_instance(cls) -> Self:
        try:
            return cls.__singleton__  # type: ignore
        except AttributeError:
            cls.__singleton__ = cls()
            return cls.__singleton__

    @classmethod
    def from_dict(
        cls, parent: T_BaseQGraphQLObject, data: dict
    ) -> T_BaseQGraphQLObject:  # pragma: no cover
        raise NotImplementedError

    def update(self, data: dict) -> Self:  # pragma: no cover
        raise NotImplementedError


T_BaseQGraphQLObject = TypeVar("T_BaseQGraphQLObject", bound=_BaseQGraphQLObject)


class QGraphQLObjectStore(Generic[T_BaseQGraphQLObject]):
    def __init__(self) -> None:
        self._data: dict[str, T_BaseQGraphQLObject] = {}

    def get_node(self, id_: str) -> Optional[T_BaseQGraphQLObject]:
        return self._data.get(id_, None)


class QGraphQListModel(QAbstractListModel, Generic[T_BaseQGraphQLObject]):
    OBJECT_ROLE = Qt.ItemDataRole.UserRole + 1
    _role_names = {OBJECT_ROLE: QByteArray("object")}  # type: ignore
    currentIndexChanged = Signal()

    def __init__(
        self,
        parent: Optional[QObject],
        default_object: T_BaseQGraphQLObject,
        data: list[T_BaseQGraphQLObject],
    ):
        super().__init__(parent)

        self._data = data
        self._default_object = default_object
        self._current_index: int = 0

    @slot
    def set_current_index(self, i: int) -> None:
        self._current_index = i
        self.currentIndexChanged.emit()

    @qproperty(int, notify=currentIndexChanged, fset=set_current_index)
    def currentIndex(self) -> int:
        return self._current_index

    @qproperty(QObject, notify=currentIndexChanged)  # type: ignore
    def currentObject(self) -> Optional[T_BaseQGraphQLObject]:
        try:
            return self._data[self._current_index]
        except IndexError:
            return self._default_object

    def rowCount(self, *args, **kwargs) -> int:
        return len(self._data)

    def roleNames(self) -> dict:
        return self._role_names  # type: ignore

    def data(self, index, role=...) -> Optional[T_BaseQGraphQLObject]:
        if index.row() < len(self._data) and index.isValid():
            if role == self.OBJECT_ROLE:
                return self._data[index.row()]
            raise NotImplementedError(
                f"role {role} is not a valid role for {self.__class__.__name__}"
            )
        return None

    def append(self, node: T_BaseQGraphQLObject) -> None:
        count = self.rowCount()
        self.beginInsertRows(self.index(count), count, count)
        self._data.append(node)
        self.endInsertRows()

    @slot
    def pop(self, index: Optional[int] = None) -> None:
        index = -1 if index is None else index
        real_index = index if index > -1 else self.rowCount()
        self.beginRemoveRows(self.index(index - 1).parent(), real_index, real_index)
        self._data.pop(index)
        self.endRemoveRows()


def get_base_graphql_object(name: str) -> type[_BaseQGraphQLObject]:
    """
    :param name: valid attribute name (used by codegen to import it).
    :returns: A type to be extended by all generated types.
    """
    type_map: dict[str, type[_BaseQGraphQLObject]] = {}
    return type(
        name, (_BaseQGraphQLObject,), {"type_map": type_map, "__store__": QGraphQLObjectStore()}
    )  # type: ignore


BaseGraphQLObject = get_base_graphql_object("BaseGraphQLObject")

T_BaseModel = TypeVar("T_BaseModel", bound=QGraphQListModel)
