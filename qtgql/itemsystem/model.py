from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Generic, Protocol, TypeVar
from uuid import UUID

import attrs
from attr import define
from PySide6 import QtCore as qtc
from PySide6.QtCore import QModelIndex

from qtgql import slot
from qtgql.exceptions import QtGqlException
from qtgql.typingref import TypeHinter

from .type_ import _TBaseType

if TYPE_CHECKING:
    from qtgql.itemsystem.schema import Schema
    from qtgql.itemsystem.type_ import BaseType


__all__ = ["NodeHelper", "NodeProto", "GenericModel"]


class RoleDoesNotExist(QtGqlException):
    ...


class NodeProto(Protocol):
    uuid: UUID | str
    Model: GenericModel


NodeT = TypeVar("NodeT", bound=NodeProto)


@attrs.define
class NodeHelper(Generic[NodeT]):
    # NOTE: This is useless if every child would have the model object as a role.
    node: NodeT
    model: GenericModel[NodeT]  # type: ignore


class GenericModel(Generic[_TBaseType], qtc.QAbstractListModel):
    """this class shouldn't be initiated directly it should be subclassed for
    every RoleDefined class."""

    __roledefined_type__: type[_TBaseType]
    __roles__: RoleMapper
    layoutAboutToBeChanged: qtc.Signal
    layoutChanged: qtc.Signal
    dataChanged: Callable[[QModelIndex, QModelIndex, list[int] | None], None]

    def __init__(self, *, schema: Schema, data: list[dict] | dict | None = None, parent=None):
        super().__init__(parent)
        self.schema = schema
        self.rowsAb = None
        self.parent_model: GenericModel | None = parent
        self.type_ = self.__roledefined_type__
        self._data: list[_TBaseType] = []
        self._child_models: list[GenericModel[Any]] = []
        if data:
            self.initialize_data(data)

    def initialize_data(self, data: list[dict] | dict) -> None:
        """

        :param data: data to generate the model

        """
        self.layoutAboutToBeChanged.emit()
        qtc.QEventLoop().processEvents()
        # search for children and initialize them as models
        for node in data:
            if children := self.__roles__.children:
                for name, child in children.items():
                    child_data = node[name]
                    child_model = child.Model(schema=self.schema, data=child_data, parent=self)
                    node[name] = child_model
                    #  save child models for further use.
                    self._child_models.append(child_model)

        # initialize list of attrs classes
        for node in data:
            node = self.type_(**node)  # type: ignore
            # cache nodes for object updates.
            if uuid := getattr(node, "uuid", None):
                self.schema.nodes[uuid] = NodeHelper(node=node, model=self)

            self._data.append(node)

        self.layoutChanged.emit()

    def data(self, index, role=...):
        if index.row() < len(self._data) and index.isValid():
            try:
                return getattr(self._data[index.row()], self.__roles__.by_num[role].name, None)
            except KeyError as exc:
                if role in (
                    -1,
                    qtc.Qt.ItemDataRole.DisplayRole,
                    qtc.Qt.ItemDataRole.ToolTipRole,
                    qtc.Qt.ItemDataRole.StatusTipRole,
                    qtc.Qt.ItemDataRole.WhatsThisRole,
                    qtc.Qt.ItemDataRole.SizeHintRole,
                    qtc.Qt.ItemDataRole.FontRole,
                    qtc.Qt.ItemDataRole.BackgroundRole,
                    qtc.Qt.ItemDataRole.ForegroundRole,
                    qtc.Qt.ItemDataRole.DecorationRole,
                    qtc.Qt.ItemDataRole.TextAlignmentRole,
                    qtc.Qt.ItemDataRole.CheckStateRole,
                ):
                    return None
                # resolvers should be pre-evaluated when the model updated
                raise RoleDoesNotExist(
                    f"role {role} of type {self.type_} at index: [{index}] "
                    f"is not a valid role!\n"
                    f"options are: {self.__roles__.qt_roles}"
                ) from exc

        return None

    def setData(self, index, value, role=...):
        if index.row() < len(self._data) and index.isValid():
            setattr(self._data[index.row()], self.__roles__.by_num[role].name, value)
            return True
        return False

    def flags(self, index):
        if index.row() < len(self._data) and index.isValid():
            return qtc.Qt.ItemFlag.ItemIsEditable
        return qtc.Qt.ItemFlag.NoItemFlags

    def roleNames(self) -> dict:
        return self.__roles__.qt_roles

    def rowCount(self, parent=...) -> int:
        return len(self._data)

    def append(self, node: _TBaseType) -> None:
        count = self.rowCount()
        self.beginInsertRows(self.index(count), count, count)
        self._data.append(node)
        self.endInsertRows()

    @slot
    def pop(self, index: int | None = None) -> None:
        index = -1 if index is None else index
        real_index = index if index > -1 else self.rowCount()
        self.beginRemoveRows(self.index(index - 1).parent(), real_index, real_index)
        self._data.pop(index)
        self.endRemoveRows()

    @slot
    def clear(self) -> None:
        if self._data:
            self.beginRemoveRows(self.index(0).parent(), 0, self.rowCount())
            for child in self._child_models:
                child.clear()
            self._data = []
            self.endRemoveRows()

    @slot
    def get_by_index(self, row: int, key: str) -> Any:
        return self.data(self.index(row), self.__roles__.by_name[key].num)

    # CLASS METHODS
    @classmethod
    def from_role_defined(
        cls, type_: type[BaseType], parent: type[GenericModel] | None = None
    ) -> type[GenericModel]:
        bases = (cls,)
        if parent:
            bases = (parent,)
        ret = type(cls.name_by_type(type_), bases, {"__roledefined_type__": type_})
        assert issubclass(ret, GenericModel)
        return ret

    @classmethod
    def name_by_type(cls, type_: type) -> str:
        return type_.__name__ + "Model"


@define
class Role:
    """Provides metadata about a field in a define_roles decorated class."""

    type: TypeHinter
    num: int
    name: str
    qt_name: qtc.QByteArray

    @classmethod
    def create(cls, name: str, role_num: int, type_: Any):
        return cls(
            type=TypeHinter.from_annotations(type_),
            num=role_num,  # not needed currently but saving here for any case
            name=name,
            qt_name=qtc.QByteArray(name.encode("utf-8")),
        )


class RoleMapper:
    """A container that maps the roles of a defined class each map has a
    certain usage in the future."""

    __slots__ = ("qt_roles", "by_name", "by_num", "qt_roles", "children", "deferred")

    def __init__(self):
        # this is the real name of the field
        # how the class would be created
        self.by_name: dict[str, Role] = {}
        # number is  a qt role 256+
        # this is how qml will call the data() method
        self.by_num: dict[int, Role] = {}
        # just to return to qt method roleNames()
        self.qt_roles: dict[int, qtc.QByteArray] = {}
        # mapping all the roledefined to know for what
        # to initialize a genericModel
        self.children: dict[str, type[BaseType]] = {}
