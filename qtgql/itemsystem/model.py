from typing import Protocol, Union, TypeVar, Generic, Callable, Optional, Any, Type, TYPE_CHECKING, ClassVar
from uuid import UUID

import attrs
from PySide6.QtCore import QModelIndex
from attr import define
from qtpy import QtCore as qtc

from qtgql import slot
from qtgql.exceptions import QtGqlException

if TYPE_CHECKING:
    from qtgql.itemsystem.role import RoleMapper, BaseRoleDefined
    from qtgql.itemsystem.schema import Schema


class RoleDoesNotExist(QtGqlException):
    ...


T = TypeVar('T')


class NodeProto(Protocol):
    uuid: Union[UUID, str]


NodeT = TypeVar('NodeT', bound=NodeProto)


@attrs.define
class NodeHelper(Generic[NodeT]):
    # NOTE: This is useless if every child would have the model object as a role.
    node: NodeT
    model: "GenericModel[NodeT]"


class GenericModel(Generic[T], qtc.QAbstractListModel):
    """
    this class shouldn't be initiated directly
     it should be subclassed for every RoleDefined class.
    """

    __roledefined_type__: "BaseRoleDefined[T]"
    layoutAboutToBeChanged: qtc.Signal
    layoutChanged: qtc.Signal
    dataChanged: Callable[[QModelIndex, QModelIndex, Optional[list[int]]], None]

    def __init__(self, *, schema: 'Schema', data: Optional[Union[list[dict], dict]] = None, parent=None):
        super().__init__(parent)
        self.schema = schema
        self.rowsAb = None
        self.parent_model: Optional['GenericModel'] = parent
        self.type_ = self.__roledefined_type__
        self.roles: RoleMapper = self.type_.__roles__
        self._data: list[T] = []
        self._child_models: list[GenericModel[Any]] = []
        if data:
            self.initialize_data(data)

    def initialize_data(self, data: Union[list[dict], dict]) -> None:
        """
        the first model will accept a dict, children will get list of dicts.
        """
        self.layoutAboutToBeChanged.emit()
        qtc.QEventLoop().processEvents()
        # search for children and initialize them as models
        for node in data:
            if children := self.roles.children:
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
                return getattr(self._data[index.row()], self.roles.by_num[role].name, None)
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
                    f"options are: {self.roles.qt_roles}"
                ) from exc

        return None

    def setData(self, index, value, role=...):
        if index.row() < len(self._data) and index.isValid():
            setattr(self._data[index.row()], self.roles.by_num[role].name, value)
            return True
        return False

    def flags(self, index):
        if index.row() < len(self._data) and index.isValid():
            return qtc.Qt.ItemFlag.ItemIsEditable
        return qtc.Qt.ItemFlag.NoItemFlags

    def roleNames(self) -> dict:
        return self.roles.qt_roles

    def rowCount(self, parent=...) -> int:
        return len(self._data)

    def append(self, node: T) -> None:
        count = self.rowCount()
        self.beginInsertRows(self.index(count), count, count)
        self._data.append(node)
        self.endInsertRows()

    def update_child(self, node: 'NodeProto'):
        if self.update_node(node):
            return

    # SLOTS:
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
            for child in self._child_models:
                child.clear()
            self._data = []
            self.endRemoveRows()

    @slot
    def get_by_index(self, row: int, key: str) -> Any:
        return self.data(self.index(row), self.roles.by_name[key].num)

    # CLASS METHODS
    @classmethod
    def from_role_defined(
            cls, type_: 'Type[BaseRoleDefined]', parent: Optional[Type["GenericModel"]] = None
    ) -> Type["GenericModel"]:
        bases = (cls,)
        if parent:
            bases = (parent,)
        ret = type(cls.name_by_type(type_), bases, {"__roledefined_type__": type_})
        assert issubclass(ret, GenericModel)
        return ret

    @classmethod
    def name_by_type(cls, type_: type) -> str:
        return type_.__name__ + "Model"
