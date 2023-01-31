from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QObject, Signal
from qtgql import qproperty
from qtgql.codegen.py.bases import BaseGraphQLObject, BaseModel
from qtgql.codegen.py.custom_scalars import DateTimeScalar


class SCALARS:
    DateTimeScalar = DateTimeScalar


class Query(BaseGraphQLObject):
    """None."""

    def __init__(
        self,
        parent: QObject = None,
        user: User = None,
    ):
        super().__init__(parent)
        self._user = user

    @classmethod
    def from_dict(cls, parent, data: dict) -> Query:
        return cls(
            parent=parent,
            user=cls.deserialize_optional_child(parent, data, User, "user"),
        )

    userChanged = Signal()

    def user_setter(self, v: User) -> None:
        self._user = v
        self.userChanged.emit()

    @qproperty(type=QObject, fset=user_setter, notify=userChanged)
    def user(self) -> User:
        return self._user


class QueryModel(BaseModel):
    def __init__(self, data: list[Query], parent: Optional[BaseGraphQLObject] = None):
        super().__init__(data, parent)


class User(BaseGraphQLObject):
    """None."""

    def __init__(
        self,
        parent: QObject = None,
        name: str = None,
        age: int = None,
        birth: SCALARS.DateTimeScalar = None,
    ):
        super().__init__(parent)
        self._name = name
        self._age = age
        self._birth = birth

    @classmethod
    def from_dict(cls, parent, data: dict) -> User:
        return cls(
            parent=parent,
            name=data.get("name", None),
            age=data.get("age", None),
            birth=SCALARS.DateTimeScalar.from_graphql(data.get("birth", None)),
        )

    nameChanged = Signal()

    def name_setter(self, v: str) -> None:
        self._name = v
        self.nameChanged.emit()

    @qproperty(type=str, fset=name_setter, notify=nameChanged)
    def name(self) -> str:
        return self._name

    ageChanged = Signal()

    def age_setter(self, v: int) -> None:
        self._age = v
        self.ageChanged.emit()

    @qproperty(type=int, fset=age_setter, notify=ageChanged)
    def age(self) -> int:
        return self._age

    birthChanged = Signal()

    def birth_setter(self, v: SCALARS.DateTimeScalar) -> None:
        self._birth = v
        self.birthChanged.emit()

    @qproperty(type=QObject, fset=birth_setter, notify=birthChanged)
    def birth(self) -> Optional[str]:
        return self._birth.to_qt()


class UserModel(BaseModel):
    def __init__(self, data: list[User], parent: Optional[BaseGraphQLObject] = None):
        super().__init__(data, parent)
