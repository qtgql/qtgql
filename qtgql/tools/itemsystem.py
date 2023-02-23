from __future__ import annotations

import types
from functools import cached_property
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Generic, Optional, Type, TypeVar, Union

import attrs
from PySide6.QtCore import QAbstractListModel, QByteArray, QEventLoop, QModelIndex, Qt, Signal
from typing_extensions import Self, dataclass_transform

from qtgql.exceptions import QtGqlException
from qtgql.tools import slot
from qtgql.utils.typingref import UNSET, TypeHinter

IS_GQL = "is_gql"
IS_ROLE = "is_role"
OLD_NAME = "old_name"

__all__ = ["role", "get_base_type", "GenericModel", "RoleDoesNotExist", "asdict"]


def asdict(t: _BaseType) -> dict:
    return attrs.asdict(t)  # type: ignore


def role(
    default=None,
    factory=UNSET,
):
    """role is optional by default."""
    if factory is not UNSET:
        default = UNSET
    return attrs.field(
        default=attrs.NOTHING if default is UNSET else default,
        factory=None if factory is UNSET else factory,
        metadata={IS_ROLE: True},
    )


def field_is(key: str, field):
    metadata = getattr(field, "metadata", {})
    return metadata.get(key, False)


T_V = TypeVar("T_V")


@dataclass_transform(
    field_descriptors=(role,),
    kw_only_default=True,
)
class BaseTypeMeta(type):
    def __new__(mcs, name, bases, ns):
        super_new = super().__new__

        # exclude BaseType itself
        parents = [b for b in bases if isinstance(b, BaseTypeMeta)]
        cls = super_new(mcs, name, bases, ns)
        if not parents:
            # remove annotations to avoid global reference errors.
            cls.__annotations__ = {}
            return cls
        if not attrs.has(cls):
            assert cls not in cls.__types_map__.values()
            cls: type[_BaseType] = attrs.define(cls, slots=True, kw_only=True)
            cls.__types_map__[cls.__name__] = cls
            roles = RoleMapper()
            for role_num, field in enumerate(attrs.fields(cls), int(Qt.ItemDataRole.UserRole)):  # type: ignore
                # assign role and check if not exists
                if field_is(IS_ROLE, field):
                    role_ = Role(
                        name=field.name, num=role_num, type_map=cls.__types_map__, type=field.type
                    )
                    # fill the role manager
                    roles.by_num[role_num] = role_
                    roles.by_name[role_.name] = role_
                    roles.qt_roles[role_.num] = role_.qt_name

            cls.Model = GenericModel.from_role_defined(cls)
            cls.Model.__roles__ = roles

        return cls


class _BaseType(metaclass=BaseTypeMeta):
    if TYPE_CHECKING:  # pragma: no cover
        __types_map__: dict[str, _BaseType]
        Model: ClassVar[type[GenericModel[Self]]]  # type: ignore

    def asdict(self) -> dict:
        return attrs.asdict(self)  # type: ignore


_TBaseType = TypeVar("_TBaseType", bound=_BaseType)

count = 1


def get_base_type() -> type[_BaseType]:
    """:return: BaseType to use for generating `GenericModel`'s"""
    global count
    cls: type[_BaseType] = types.new_class(
        name=f"BaseType{count}", kwds={"metaclass": BaseTypeMeta}
    )
    # we need to inject this here in order for `get_type_hints()` to work.
    cls.__types_map__ = {GenericModel.__name__: GenericModel}  # type: ignore
    count += 1
    return cls


class Role:
    """Provides metadata about a field in a define_roles decorated class."""

    __slots__ = ("num", "name", "qt_name", "_type", "str_type", "type_map")

    def __init__(self, num: int, name: str, type: Union[TypeHinter, str], type_map: dict):
        self.num = num
        self.name = name
        self.qt_name = QByteArray(name.encode("utf-8"))
        self.type_map = type_map
        if isinstance(type, str):
            self.str_type = type
        else:
            self._type = TypeHinter.from_annotations(type)

    @property
    def type(self) -> TypeHinter:
        try:
            return self._type
        except AttributeError:
            self._type = TypeHinter.from_string(self.str_type, ns=self.type_map)
            return self._type


class RoleMapper:
    """A container that maps the roles of a defined class each map has a
    certain usage in the future."""

    def __init__(self) -> None:
        # this is the real name of the field
        # how the class would be created
        self.by_name: dict[str, Role] = {}
        # number is  a qt role 256+
        # this is how qml will call the data() method
        self.by_num: dict[int, Role] = {}
        # just to return to qt method roleNames()
        self.qt_roles: dict[int, QByteArray] = {}

    @cached_property
    def children(self) -> dict[str, type[_BaseType]]:
        # mapping all the roledefined to know for what
        # to initialize a genericModel
        ret = {}
        for role_ in self.by_name.values():
            # lists must be child models
            if role_.type.type is GenericModel:
                child_type = role_.type.of_type[0].type
                ret[role_.name] = child_type
        return ret


class RoleDoesNotExist(QtGqlException):
    ...


class GenericModel(Generic[_TBaseType], QAbstractListModel):
    """Contains logic autogenerated models that extends `_BaseType` You don't
    need to use this class directly.

    Although you would need it to annotate "child" roles. i.e:

    ```python
    from qtgql.tools.itemsystem import get_base_type, GenericModel

    BaseType = get_base_type()
    class SomeModel(BaseType):
         other_model: GenericModel['OtherModel']
    ```
    """

    __roledefined_type__: type[_TBaseType]
    __roles__: RoleMapper
    layoutAboutToBeChanged: Signal
    layoutChanged: Signal
    dataChanged: Callable[[QModelIndex, QModelIndex, Optional[list[int]]], None]

    def __init__(self, *, data: Optional[Union[list[dict], dict]] = None, parent=None):
        super().__init__(parent)
        self.rowsAb = None
        self.parent_model: Optional[GenericModel] = parent
        self.type_ = self.__roledefined_type__
        self._data: list[_TBaseType] = []
        self._child_models: list[GenericModel[Any]] = []
        if data:
            self.initialize_data(data)

    def initialize_data(self, data: Union[list[dict], dict]) -> None:
        """:param data: data to generate the model"""
        self.layoutAboutToBeChanged.emit()
        QEventLoop().processEvents()
        # search for children and initialize them as models
        for node in data:
            if children := self.__roles__.children:
                for name, child in children.items():
                    child_data = node[name]
                    child_model = child.Model(data=child_data, parent=self)
                    node[name] = child_model
                    #  save child models for further use.
                    self._child_models.append(child_model)

        # initialize list of attrs classes
        for node in data:
            node = self.type_(**node)  # type: ignore
            self._data.append(node)

        self.layoutChanged.emit()

    def data(self, index, role=...):
        if index.row() < len(self._data) and index.isValid():
            try:
                return getattr(self._data[index.row()], self.__roles__.by_num[role].name, None)
            except KeyError as exc:
                if role in (
                    -1,
                    Qt.ItemDataRole.DisplayRole,
                    Qt.ItemDataRole.ToolTipRole,
                    Qt.ItemDataRole.StatusTipRole,
                    Qt.ItemDataRole.WhatsThisRole,
                    Qt.ItemDataRole.SizeHintRole,
                    Qt.ItemDataRole.FontRole,
                    Qt.ItemDataRole.BackgroundRole,
                    Qt.ItemDataRole.ForegroundRole,
                    Qt.ItemDataRole.DecorationRole,
                    Qt.ItemDataRole.TextAlignmentRole,
                    Qt.ItemDataRole.CheckStateRole,
                ):
                    return None
                # resolvers should be pre-evaluated when the model updated
                raise RoleDoesNotExist(
                    f"role {role} of type {self.type_} at index: [{index}] "
                    f"is not a valid role!\n"
                    f"options are: {self.__roles__.qt_roles}"
                ) from exc

    def setData(self, index, value, role=...):
        if index.row() < len(self._data) and index.isValid():
            setattr(self._data[index.row()], self.__roles__.by_num[role].name, value)
            return True
        return False

    def flags(self, index):
        if index.row() < len(self._data) and index.isValid():
            return Qt.ItemFlag.ItemIsEditable
        return Qt.ItemFlag.NoItemFlags

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
        return self.data(self.index(row), self.__roles__.by_name[key].num)

    # CLASS METHODS
    @classmethod
    def from_role_defined(
        cls, type_: type[_BaseType], parent: Optional[Type[GenericModel]] = None
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
