from __future__ import annotations

import dataclasses
from typing import ClassVar, TypeVar

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
    qt_name: qtc.QByteArray

    @classmethod
    def create(cls, name: str, role_num: int, type_: type):
        return cls(
            type=TypeHinter.from_annotations(type_),
            num=role_num,  # not needed currently but saving here for any case
            name=name,
            qt_name=qtc.QByteArray(name.encode("utf-8")),
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
        self.by_name: dict[str, Role] = {}
        # number is  a qt role 256+
        # this is how qml will call the data() method
        self.by_num: dict[int, Role] = {}
        # just to return to qt method roleNames()
        self.qt_roles: dict[int, qtc.QByteArray] = {}
        # mapping all the roledefined to know for what
        # to initialize a genericModel
        self.children: dict[str, type[BaseRoleDefined]] = {}
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


class TypesStorage(dict):
    def add(self, type_: type[BaseRoleDefined]):
        super().__setitem__(type_.__name__, type_)

    @dataclass_transform(
        field_descriptors=(attr.attrib, attr.field, role),
    )
    def register(self, t: type) -> type[BaseRoleDefined]:
        t = dataclasses.dataclass(t)
        self.add(t)
        return t

    def __setitem__(self, key, value):
        raise NotImplementedError


class BaseRoleDefined:
    Model: type[GenericModel[Self]]
    __roles__: ClassVar[RoleMapper]
