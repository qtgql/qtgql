from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, ClassVar, Generic, NamedTuple, Optional, TypeVar

from PySide6.QtCore import QAbstractListModel, QByteArray, QObject, Qt, Signal, Slot

if TYPE_CHECKING:
    from typing_extensions import Self

    from qtgql.codegen.py.runtime.queryhandler import OperationMetaData, SelectionConfig
from qtgql.tools import qproperty, slot

__all__ = ["QGraphQListModel", "get_base_graphql_object"]


class QGraphQLInputObjectABC(QObject):
    def asdict(self) -> dict:
        raise NotImplementedError


class _BaseQGraphQLObject(QObject):
    _id: str
    id: str
    __singleton__: Self
    __store__: ClassVar[QGraphQLObjectStore[Self]]

    def __init_subclass__(cls, **kwargs):
        cls.__store__ = QGraphQLObjectStore()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

    @qproperty(str, constant=True)
    def typename(self) -> str:
        return self.__class__.__name__

    @classmethod
    def from_dict(cls, parent: QObject, data: dict, config: SelectionConfig):
        """Creates a new instance from GraphQL raw data."""
        raise NotImplementedError

    def update(self, data, config: SelectionConfig) -> None:
        """updates a node based on new GraphQL data."""
        raise NotImplementedError

    def loose(self, metadata: OperationMetaData) -> None:
        """releases all child objects if exists.

        note that this method would be useful only if the object (or one
        of its children) has an id and a reference in the store,
        otherwise the pointer to this object is release and this object
        would be deleted.
        """
        raise NotImplementedError

    @classmethod
    def default_instance(cls) -> Self:
        # used for default values.
        try:
            return cls.__singleton__  # type: ignore
        except AttributeError:
            cls.__singleton__ = cls()
            return cls.__singleton__


T_BaseQGraphQLObject = TypeVar("T_BaseQGraphQLObject", bound=_BaseQGraphQLObject)


class NodeRecord(NamedTuple):
    node: _BaseQGraphQLObject
    retainers: set[str]  # set of operation names.

    def retain(self, operation_name: str) -> Self:
        self.retainers.add(operation_name)
        return self


class QGraphQLObjectStore(Generic[T_BaseQGraphQLObject]):
    def __init__(self) -> None:
        self._data: dict[str, NodeRecord] = {}

    def get_node(self, id_: str) -> Optional[_BaseQGraphQLObject]:
        assert id_
        if found := self._data.get(id_, None):
            return found.node

    def add_record(self, record: NodeRecord):
        assert record.node.id
        self._data[record.node.id] = record

    def loose(self, node: T_BaseQGraphQLObject, operation_name: str) -> None:
        assert node.id
        with contextlib.suppress(
            KeyError,
        ):  # This node was already deleted, we can safely ignore it
            record = self._data[node.id]
            record.retainers.remove(operation_name)
            if not record.retainers:
                self._data.pop(node.id)
                node.deleteLater()  # we can delete it now since it has no retainers.


class QGraphQListModel(QAbstractListModel, Generic[T_BaseQGraphQLObject]):
    OBJECT_ROLE = Qt.ItemDataRole.UserRole + 1
    _role_names = {OBJECT_ROLE: QByteArray("object")}  # type: ignore
    currentIndexChanged = Signal()

    def __init__(
        self,
        parent: Optional[QObject],
        data: list[T_BaseQGraphQLObject],
    ):
        super().__init__(parent)
        self._data = data
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
        return self._data[self._current_index]

    def rowCount(self, *args, **kwargs) -> int:
        return len(self._data)

    def roleNames(self) -> dict:
        return self._role_names  # type: ignore

    def data(self, index, role=...) -> Optional[T_BaseQGraphQLObject]:
        if index.row() < len(self._data) and index.isValid():
            if role == self.OBJECT_ROLE:
                return self._data[index.row()]
            raise NotImplementedError(
                f"role {role} is not a valid role for {self.__class__.__name__}",
            )

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

    @slot
    def clear(self) -> None:
        if self._data:
            self.beginRemoveRows(self.index(0).parent(), 0, self.rowCount())
            self._data = []
            self.endRemoveRows()

    @Slot(int, QObject)
    def insert(self, index: int, v: T_BaseQGraphQLObject):
        model_index = self.index(index)
        if index <= self.rowCount() - 1:
            self.beginInsertRows(model_index, index, index)
            self._data[index] = v
            self.endInsertRows()
        else:
            model_index = self.index(self.rowCount() - 1)
            index = self.rowCount()
            self.beginInsertRows(model_index, index, index)
            self._data.append(v)
            self.endInsertRows()

    def update(self, data: list[dict], node_selection: SelectionConfig) -> None:
        raise NotImplementedError

    def removeRows(self, row: int, count: int, parent=None) -> bool:
        # check that this is a valid removal.
        if row + count <= self.rowCount():
            self.beginRemoveRows(self.index(0).parent(), row, count)
            end = self._data[row + count :]
            start = self._data[:row]
            self._data = start + end
            self.endRemoveRows()
            return True
        return False  # pragma: no cover


def get_base_graphql_object(name: str) -> type[_BaseQGraphQLObject]:
    """
    :param name: valid attribute name (used by codegen to import it).
    :returns: A type to be extended by all generated types.
    """
    return type(name, (_BaseQGraphQLObject,), {"__store__": QGraphQLObjectStore()})  # type: ignore


BaseGraphQLObject = get_base_graphql_object("BaseGraphQLObject")

T_BaseModel = TypeVar("T_BaseModel", bound=QGraphQListModel)
