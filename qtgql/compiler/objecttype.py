from typing import Generic, Optional, Type, TypeVar

from attrs import define, field

T = TypeVar("T")


@define
class PropertyImpl(Generic[T]):
    name: str
    type: Type[T] = field(converter=lambda v: v.__name__)
    default: Optional[T] = None

    @property
    def setter_name(self) -> str:
        return self.name + "_setter"

    @property
    def signal_name(self) -> str:
        return self.name + "Changed"

    @property
    def private_name(self) -> str:
        return "_" + self.name


@define
class GqlType:
    name: str
    properties: list[PropertyImpl]
    docstring: Optional[str] = ""
