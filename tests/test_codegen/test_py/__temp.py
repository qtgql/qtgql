from __future__ import annotations

from enum import Enum, auto
from typing import Optional

from PySide6.QtCore import QEnum, QObject, Signal
from PySide6.QtQml import QmlElement
from qtgql import qproperty
from qtgql.codegen.py.bases import BaseGraphQLObject, BaseModel
from qtgql.codegen.py.custom_scalars import DateScalar, DateTimeScalar, DecimalScalar, TimeScalar

QML_IMPORT_NAME = "QtGql"
QML_IMPORT_MAJOR_VERSION = 1


class Status(Enum):
    Connected = auto()
    """None."""
    Stale = auto()
    """None."""
    Disconnected = auto()
    """None."""


@QmlElement
class Enums(QObject):
    QEnum(Status)


class SCALARS:
    DateTimeScalar = DateTimeScalar
    DecimalScalar = DecimalScalar
    DateScalar = DateScalar
    TimeScalar = TimeScalar


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
        status: Status = None,
    ):
        super().__init__(parent)
        self._name = name
        self._age = age
        self._status = status

    @classmethod
    def from_dict(cls, parent, data: dict) -> User:
        return cls(
            parent=parent,
            name=data.get("name", None),
            age=data.get("age", None),
            status=Status[data.get("status", 1)],
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

    statusChanged = Signal()

    def status_setter(self, v: Status) -> None:
        self._status = v
        self.statusChanged.emit()

    @qproperty(type=int, fset=status_setter, notify=statusChanged)
    def status(self) -> int:
        return self._status


class UserModel(BaseModel):
    def __init__(self, data: list[User], parent: Optional[BaseGraphQLObject] = None):
        super().__init__(data, parent)
