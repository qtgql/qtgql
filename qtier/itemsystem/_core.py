from typing import (
    Any,
    Callable,
    ClassVar,
    Generic,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
    get_args,
)

import attr as attr
import attrs
from attrs import NOTHING, asdict, define
from qtpy import QtCore as qtc
from qtpy.QtCore import QModelIndex
from typing_extensions import dataclass_transform

from qtier import slot
from qtier.exceptions import QtHackException

UNSET = TypeVar("UNSET")
IS_GQL = "is_gql"
IS_ROLE = "is_role"
OLD_NAME = "old_name"
T = TypeVar("T")


class RoleDoesNotExist(QtHackException):
    ...


@define
class Role:
    """
    provides metadata about a field in a define_roles decorated class
    """

    type: Any  # noqa: A003
    num: int
    name: str
    python_name: str
    qt_name: qtc.QByteArray
    field: attrs.Attribute
    is_child: Optional[bool] = None

    @classmethod
    def from_field(cls, field: attrs.Attribute, role_num: int, python_name: str):
        return cls(
            type=field.type,
            num=role_num,  # not needed currently but saving here for any case
            name=field.name,
            qt_name=qtc.QByteArray(python_name.encode("utf-8")),
            python_name=python_name,
            field=field,
            is_child=is_role_defined(field.type),
        )


@define
class RoleMapper:
    """
    A container that maps the roles of a defined class
    each map has a certain usage in the future.
    """

    # this is the real name of the field
    # how the class would be created
    by_name: dict[str, "Role"] = attrs.field(factory=dict)
    # number is  a qt role 256+
    # this is how qml will call the data() method
    by_num: dict[int, Role] = attrs.field(factory=dict)
    # just to return to qt method roleNames()
    qt_roles: dict[int, qtc.QByteArray] = attrs.field(factory=dict)
    # mapping all the roledefined to know for what
    # to initialize a genericModel
    children: dict[str, "Role"] = attrs.field(factory=dict)


class RoleDefined(Generic[T]):
    __roles__: ClassVar["RoleMapper"]
    Model: Type["GenericModel[T]"]


BaseRoleDefined = TypeVar("BaseRoleDefined", bound=RoleDefined, covariant=True)


def item_asdict(item) -> dict:
    return asdict(item)  # type: ignore


def field_is(key: str, field):
    metadata = getattr(field, "metadata", {})
    return metadata.get(key, False)


def is_role_defined(type_):
    if inner := get_args(type_):
        type_ = inner[0]
    return issubclass(type_, RoleDefined)


def create_roles(cls: Type[RoleDefined], fields: list[attrs.Attribute]) -> list[attrs.Attribute]:
    roles = RoleMapper()
    for role_num, field in enumerate(fields, int(qtc.Qt.ItemDataRole.UserRole)):
        # assign role and check if not exists
        python_name = field.name
        if field_is(IS_ROLE, field):
            role_ = Role.from_field(field, role_num, python_name)
            # fill the role manager
            roles.by_num[role_num] = role_
            roles.by_name[role_.name] = role_
            roles.qt_roles[role_.num] = role_.qt_name
            if role_.is_child:
                roles.children[role_.name] = role_

    cls.__roles__ = roles

    return fields


def role(
    is_gql=True,
    default=NOTHING,
    factory=None,
    validator=None,
    converter=None,
    eq=True,
    order=None,
    init=False,
    metadata=None,
):
    return attrs.field(
        default=default,
        factory=factory,
        validator=validator,
        repr=True,  # noqa: A002
        converter=converter,
        eq=eq,
        order=order,
        hash=None,
        init=init if init else is_gql,
        metadata=metadata if metadata else {IS_GQL: is_gql, IS_ROLE: True},
    )


@dataclass_transform(
    field_descriptors=(attr.attrib, attr.field, role),
)
def define_roles(cls: Union[Type[T], Type[RoleDefined]]) -> Type[BaseRoleDefined]:
    ns = cls.__dict__.copy()
    # if defined a model in order to override stuff.
    if model := getattr(cls, "Model", None):
        assert issubclass(model, GenericModel)
    bases = cls.__bases__ if cls.__bases__ != (object,) else (RoleDefined,)
    ns["Model"] = model
    cls = cast(
        Type[BaseRoleDefined],
        attrs.define(type(cls.__name__, bases, ns), field_transformer=create_roles, kw_only=True),
    )
    # parent maybe None.
    cls.Model = GenericModel.from_role_defined(cls, parent=model)
    return cls


@define
class NodeHelper(Generic[T]):
    # NOTE: This is useless if every child would have the model object as a role.
    node: T
    model: "GenericModel[T]"


class GenericModel(Generic[T], qtc.QAbstractListModel):
    """
    this class shouldn't be initiated directly
     it should be subclassed for every RoleDefined class
     because caching for all types is not wanted if a model provides
     certain logic.
    """

    __roledefined_type__: RoleDefined[T]
    layoutAboutToBeChanged: qtc.Signal
    layoutChanged: qtc.Signal
    dataChanged: Callable[[QModelIndex, QModelIndex, Optional[list[int]]], None]
    _nodes: dict[str, NodeHelper[T]] = {}

    def __init__(self, data: Optional[Union[list[dict], dict]] = None, parent=None):
        super().__init__(parent)
        self.rowsAb = None
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
                    child_model = child.type.Model(child_data, parent=self)
                    node[name] = child_model
                    #  save child models for further use.
                    self._child_models.append(child_model)

        # initialize list of attrs classes
        for node in data:
            node = self.type_(**node)  # type: ignore
            # cache nodes for object updates.
            if uuid := getattr(node, "uuid", None):
                self._nodes[uuid] = NodeHelper(node=node, model=self)

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

    def get_node(self, uuid: str) -> Optional[NodeHelper[T]]:
        return self._nodes.get(uuid, None)

    def update_node(self, uuid: str, node: T) -> None:
        node_helper = self._nodes[uuid]
        model = node_helper.model
        node_model_index = model._data.index(node_helper.node)
        # replace old node
        model._data[node_model_index] = node
        self._nodes[uuid].node = node
        # notify changes
        index = model.index(node_model_index)
        model.dataChanged.emit(index, index)  # type: ignore

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

    @classmethod
    def from_role_defined(
        cls, type_: Type[RoleDefined], parent: Optional[Type["GenericModel"]] = None
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
