from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

from attr import define

T = TypeVar("T")

__all__ = ["BaseCustomScalar", "BuiltinScalars"]


class BaseCustomScalar(Generic[T], ABC):
    """Class to extend by user defined scalars."""

    __slots__ = "_value"
    GRAPHQL_NAME: str
    """The *real* GraphQL name of the scalar (used by the codegen inspection
    pipeline)."""
    DEFAULT_VALUE: T
    """A place holder graphql query returned null or the field wasn't queried.

    can be used by `from_graphql()`
    """

    def __init__(self, v: Optional[T] = None):
        if not v:
            self._value = self.DEFAULT_VALUE
        else:
            self._value = v

    @abstractmethod
    def from_graphql(cls, v: Optional[Any] = None) -> "BaseCustomScalar":
        """Deserializes data fetched from graphql, This is useful when you want
        to set a first-of value that will later be used by `to_qt()`.

        **must be overridden**!
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def to_qt(self) -> Any:
        """Will be used by the property getter, This is the official value that
        Qt should "understand".

        **must be overridden**!
        """
        raise NotImplementedError  # pragma: no cover


@define
class BuiltinScalar:
    tp: type
    default_value: Any
    graphql_name: str


class BuiltinScalars:
    scalars = [
        BuiltinScalar(int, 0, graphql_name="Int"),
        BuiltinScalar(float, 0.0, graphql_name="Float"),
        BuiltinScalar(str, " - ", graphql_name="String"),
        BuiltinScalar(str, "", graphql_name="ID"),
        BuiltinScalar(bool, False, "Boolean"),
        BuiltinScalar(str, "", "UUID"),
    ]

    @classmethod
    def by_graphql_name(cls, name: str) -> Optional[BuiltinScalar]:
        for scalar in cls.scalars:
            if scalar.graphql_name == name:
                return scalar

    @classmethod
    def by_python_type(cls, tp: type) -> Optional[BuiltinScalar]:
        for scalar in cls.scalars:
            if scalar.tp is tp:
                return scalar

    _keys = [scalar.graphql_name for scalar in scalars]

    @classmethod
    def keys(cls) -> list[str]:
        return cls._keys
