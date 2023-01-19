from __future__ import annotations

import types
from typing import TYPE_CHECKING, ClassVar, TypeVar

import attrs
from typing_extensions import Self, dataclass_transform

from qtgql.typingref import UNSET

if TYPE_CHECKING:
    from .model import GenericModel

IS_GQL = "is_gql"
IS_ROLE = "is_role"
OLD_NAME = "old_name"


def role(
    default=None,
    factory=UNSET,
):
    """role is optional by default.

    this will be changed in the future when we will implement schema
    generation.
    """
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


class TypesStore(dict[str, type[T_V]]):
    def add(self, type_: type[T_V]):
        super().__setitem__(type_.__name__, type_)

    def __setitem__(self, key, value):
        raise NotImplementedError


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
            cls: type[BaseType] = attrs.define(cls, slots=True, kw_only=True)
            cls.__types_store__.add(cls)
        return cls


class BaseType(metaclass=BaseTypeMeta):
    __types_store__: TypesStore[BaseType] = TypesStore()
    Model: ClassVar[type[GenericModel[Self]]]  # type: ignore

    def asdict(self) -> dict:
        return attrs.asdict(self)  # type: ignore


_TBaseType = TypeVar("_TBaseType", bound=BaseType)

count = 1


def get_base_type() -> type[BaseType]:
    global count
    cls: type[BaseType] = types.new_class(name=f"BaseType{count}", kwds={"metaclass": BaseTypeMeta})
    cls.__types_store__ = TypesStore()
    count += 1
    return cls
