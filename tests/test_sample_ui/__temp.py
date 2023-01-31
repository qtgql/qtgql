from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QObject, Signal
from qtgql import qproperty
from qtgql.codegen.py.bases import BaseGraphQLObject, BaseModel
from qtgql.codegen.py.custom_scalars import DateScalar, DateTimeScalar, DecimalScalar


class SCALARS:
    DateTimeScalar = DateTimeScalar

    DecimalScalar = DecimalScalar

    DateScalar = DateScalar


class Query(BaseGraphQLObject):
    """None."""

    def __init__(
        self,
        parent: QObject = None,
        hello: str = None,
        isAuthenticated: str = None,
        apples: list[Apple] = None,
    ):
        super().__init__(parent)
        self._hello = hello
        self._isAuthenticated = isAuthenticated
        self._apples = apples

    @classmethod
    def from_dict(cls, parent, data: dict) -> Query:
        return cls(
            parent=parent,
            hello=data.get("hello", None),
            isAuthenticated=data.get("isAuthenticated", None),
            apples=cls.deserialize_list_of(parent, data, AppleModel, "apples", Apple),
        )

    helloChanged = Signal()

    def hello_setter(self, v: str) -> None:
        self._hello = v
        self.helloChanged.emit()

    @qproperty(type=str, fset=hello_setter, notify=helloChanged)
    def hello(self) -> str:
        return self._hello

    isAuthenticatedChanged = Signal()

    def isAuthenticated_setter(self, v: str) -> None:
        self._isAuthenticated = v
        self.isAuthenticatedChanged.emit()

    @qproperty(type=str, fset=isAuthenticated_setter, notify=isAuthenticatedChanged)
    def isAuthenticated(self) -> str:
        return self._isAuthenticated

    applesChanged = Signal()

    def apples_setter(self, v: list[Apple]) -> None:
        self._apples = v
        self.applesChanged.emit()

    @qproperty(type=QObject, fset=apples_setter, notify=applesChanged)
    def apples(self) -> AppleModel:
        return self._apples


class QueryModel(BaseModel):
    def __init__(self, data: list[Query], parent: Optional[BaseGraphQLObject] = None):
        super().__init__(data, parent)


class Apple(BaseGraphQLObject):
    """None."""

    def __init__(
        self,
        parent: QObject = None,
        size: int = None,
        owner: str = None,
        worms: Optional[list[Worm]] = None,
        color: str = None,
    ):
        super().__init__(parent)
        self._size = size
        self._owner = owner
        self._worms = worms
        self._color = color

    @classmethod
    def from_dict(cls, parent, data: dict) -> Apple:
        return cls(
            parent=parent,
            size=data.get("size", None),
            owner=data.get("owner", None),
            worms=cls.deserialize_list_of(parent, data, WormModel, "worms", Worm),
            color=data.get("color", None),
        )

    sizeChanged = Signal()

    def size_setter(self, v: int) -> None:
        self._size = v
        self.sizeChanged.emit()

    @qproperty(type=int, fset=size_setter, notify=sizeChanged)
    def size(self) -> int:
        return self._size

    ownerChanged = Signal()

    def owner_setter(self, v: str) -> None:
        self._owner = v
        self.ownerChanged.emit()

    @qproperty(type=str, fset=owner_setter, notify=ownerChanged)
    def owner(self) -> str:
        return self._owner

    wormsChanged = Signal()

    def worms_setter(self, v: Optional[list[Worm]]) -> None:
        self._worms = v
        self.wormsChanged.emit()

    @qproperty(type=QObject, fset=worms_setter, notify=wormsChanged)
    def worms(self) -> WormModel:
        return self._worms

    colorChanged = Signal()

    def color_setter(self, v: str) -> None:
        self._color = v
        self.colorChanged.emit()

    @qproperty(type=str, fset=color_setter, notify=colorChanged)
    def color(self) -> str:
        return self._color


class AppleModel(BaseModel):
    def __init__(self, data: list[Apple], parent: Optional[BaseGraphQLObject] = None):
        super().__init__(data, parent)


class Worm(BaseGraphQLObject):
    """None."""

    def __init__(
        self,
        parent: QObject = None,
        name: str = None,
        family: str = None,
        size: int = None,
    ):
        super().__init__(parent)
        self._name = name
        self._family = family
        self._size = size

    @classmethod
    def from_dict(cls, parent, data: dict) -> Worm:
        return cls(
            parent=parent,
            name=data.get("name", None),
            family=data.get("family", None),
            size=data.get("size", None),
        )

    nameChanged = Signal()

    def name_setter(self, v: str) -> None:
        self._name = v
        self.nameChanged.emit()

    @qproperty(type=str, fset=name_setter, notify=nameChanged)
    def name(self) -> str:
        return self._name

    familyChanged = Signal()

    def family_setter(self, v: str) -> None:
        self._family = v
        self.familyChanged.emit()

    @qproperty(type=str, fset=family_setter, notify=familyChanged)
    def family(self) -> str:
        return self._family

    sizeChanged = Signal()

    def size_setter(self, v: int) -> None:
        self._size = v
        self.sizeChanged.emit()

    @qproperty(type=int, fset=size_setter, notify=sizeChanged)
    def size(self) -> int:
        return self._size


class WormModel(BaseModel):
    def __init__(self, data: list[Worm], parent: Optional[BaseGraphQLObject] = None):
        super().__init__(data, parent)


class Mutation(BaseGraphQLObject):
    """None."""

    def __init__(
        self,
        parent: QObject = None,
        pseudoMutation: bool = None,
    ):
        super().__init__(parent)
        self._pseudoMutation = pseudoMutation

    @classmethod
    def from_dict(cls, parent, data: dict) -> Mutation:
        return cls(
            parent=parent,
            pseudoMutation=data.get("pseudoMutation", None),
        )

    pseudoMutationChanged = Signal()

    def pseudoMutation_setter(self, v: bool) -> None:
        self._pseudoMutation = v
        self.pseudoMutationChanged.emit()

    @qproperty(type=bool, fset=pseudoMutation_setter, notify=pseudoMutationChanged)
    def pseudoMutation(self) -> bool:
        return self._pseudoMutation


class MutationModel(BaseModel):
    def __init__(self, data: list[Mutation], parent: Optional[BaseGraphQLObject] = None):
        super().__init__(data, parent)


class Subscription(BaseGraphQLObject):
    """None."""

    def __init__(
        self,
        parent: QObject = None,
        count: int = None,
    ):
        super().__init__(parent)
        self._count = count

    @classmethod
    def from_dict(cls, parent, data: dict) -> Subscription:
        return cls(
            parent=parent,
            count=data.get("count", None),
        )

    countChanged = Signal()

    def count_setter(self, v: int) -> None:
        self._count = v
        self.countChanged.emit()

    @qproperty(type=int, fset=count_setter, notify=countChanged)
    def count(self) -> int:
        return self._count


class SubscriptionModel(BaseModel):
    def __init__(self, data: list[Subscription], parent: Optional[BaseGraphQLObject] = None):
        super().__init__(data, parent)
