from collections import defaultdict
import dataclasses
from typing import ClassVar, NamedTuple, Type, TypeVar

import attr as attr
from attrs import define
from qtpy import QtCore as qtc
from typing_extensions import Self, dataclass_transform

from qtgql.typingref import UNSET, TypeHinter

from .model import GenericModel

IS_GQL = "is_gql"
IS_ROLE = "is_role"
OLD_NAME = "old_name"
T = TypeVar("T")


@define
class Role:
    """
    provides metadata about a field in a define_roles decorated class
    """

    type: TypeHinter  # noqa: A003
    num: int
    name: str
    python_name: str
    qt_name: qtc.QByteArray
    field: dataclasses.Field

    @classmethod
    def from_field(cls, field: dataclasses.Field, role_num: int, python_name: str):
        return cls(
            type=TypeHinter.from_annotations(field.type),
            num=role_num,  # not needed currently but saving here for any case
            name=field.name,
            qt_name=qtc.QByteArray(python_name.encode("utf-8")),
            python_name=python_name,
            field=field,
        )


class RoleMapper:
    """
    A container that maps the roles of a defined class
    each map has a certain usage in the future.
    """

    __slots__ = ("qt_roles", "by_name", "by_num", "qt_roles", "children", "deferred")

    def __init__(self):
        # this is the real name of the field
        # how the class would be created
        self.by_name: dict[str, "Role"] = {}
        # number is  a qt role 256+
        # this is how qml will call the data() method
        self.by_num: dict[int, Role] = {}
        # just to return to qt method roleNames()
        self.qt_roles: dict[int, qtc.QByteArray] = {}
        # mapping all the roledefined to know for what
        # to initialize a genericModel
        self.children: dict[str, "Type[BaseRoleDefined]"] = {}
        self.deferred: dict[str, str] = {}


def role(
    default=None,
    factory=UNSET,
):
    """
    role is optional by default.
    this will be changed in the future when we will implement schema generation.
    """
    if factory:
        default = UNSET
    return dataclasses.field(
        default=dataclasses.MISSING if default is UNSET else default,
        default_factory=factory if factory else dataclasses.MISSING,
        metadata={IS_ROLE: True},
    )


def field_is(key: str, field):
    metadata = getattr(field, "metadata", {})
    return metadata.get(key, False)


class RoleDefinedMeta(type):
    Model: "Type[GenericModel[Self]]"
    __roles__: ClassVar[RoleMapper]

    def __new__(mcs, name, bases, dct):
        cls = super().__new__(mcs, name, bases, dct)
        # the original base class should not be @defined...
        # and avoid recursion
        if bases and not dataclasses.is_dataclass(cls):
            cls = dataclasses.dataclass(cls, kw_only=True, slots=True)
            cls: "BaseRoleDefined"
            roles = RoleMapper()
            for role_num, field in enumerate(
                dataclasses.fields(cls), int(qtc.Qt.ItemDataRole.UserRole)
            ):
                # assign role and check if not exists
                python_name = field.name
                if field_is(IS_ROLE, field):
                    role_ = Role.from_field(field, role_num, python_name)
                    # fill the role manager
                    roles.by_num[role_num] = role_
                    roles.by_name[role_.name] = role_
                    roles.qt_roles[role_.num] = role_.qt_name
                    # lists must be child models
                    if role_.type.type is list:
                        child_type = role_.type.of_type[0].type
                        # find forward references
                        if isinstance(child_type, str):
                            cls.__deferred_types__[child_type].append(
                                DeferredRole(role=role_, parent=cls)
                            )
                        else:
                            assert issubclass(child_type, BaseRoleDefined)
                            roles.children[role_.name] = child_type

            cls.__roles__ = roles
            cls.Model = GenericModel.from_role_defined(cls)
        return cls


class TypesStorage(dict):
    def add(self, type_: Type["BaseRoleDefined"]):
        super().__setitem__(type_.__name__, type_)

    def __setitem__(self, key, value):
        raise NotImplementedError


class DeferredRole(NamedTuple):
    role: Role
    parent: "BaseRoleDefined"


@dataclass_transform(
    field_descriptors=(attr.attrib, attr.field, role),
)
class BaseRoleDefined(metaclass=RoleDefinedMeta):
    __types_store__: TypesStorage = TypesStorage()
    __deferred_types__: dict[str, list[DeferredRole]] = defaultdict(list)

    def __init_subclass__(cls, **kwargs):
        cls.__types_store__.add(cls)
        if detained_list := cls.__deferred_types__.get(cls.__name__, None):
            for detained in detained_list:
                detained.parent.__roles__.children[detained.role.name] = cls

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)
