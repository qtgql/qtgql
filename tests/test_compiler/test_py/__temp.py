from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal
from qtgql.compiler.py.bases import BaseModel, BaseQGraphQLObject


class Query(BaseQGraphQLObject):
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
            user=User.from_dict(parent, data["user"]),
        )

    userChanged = Signal()

    def user_setter(self, v: User) -> None:
        self._user = v
        self.userChanged.emit()

    @Property(type="QVariant", fset=user_setter, notify=userChanged)
    def user(self) -> User:
        return self._user


class QueryModel(BaseModel):
    def __init__(self, data: list[Query], parent: BaseQGraphQLObject | None = None):
        super().__init__(data, parent)


class User(BaseQGraphQLObject):
    """None."""

    def __init__(
        self,
        parent: QObject = None,
        name: str = None,
        age: str = None,
    ):
        super().__init__(parent)
        self._name = name
        self._age = age

    @classmethod
    def from_dict(cls, parent, data: dict) -> User:
        return cls(
            parent=parent,
            name=data["name"],
            age=data["age"],
        )

    nameChanged = Signal()

    def name_setter(self, v: str) -> None:
        self._name = v
        self.nameChanged.emit()

    @Property(type=str, fset=name_setter, notify=nameChanged)
    def name(self) -> str:
        return self._name

    ageChanged = Signal()

    def age_setter(self, v: str) -> None:
        self._age = v
        self.ageChanged.emit()

    @Property(type=str, fset=age_setter, notify=ageChanged)
    def age(self) -> str:
        return self._age


class UserModel(BaseModel):
    def __init__(self, data: list[User], parent: BaseQGraphQLObject | None = None):
        super().__init__(data, parent)
