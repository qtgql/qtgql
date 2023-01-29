from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from qtgql import qproperty
from qtgql.codegen.py.bases import BaseModel
from qtgql.codegen.py.scalars import DateTimeScalar
from qtgql.itemsystem.core import DefaultBaseType


class SCALARS:
    DateTimeScalar = DateTimeScalar


class Query(DefaultBaseType):
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
    def user(self):
        return self._user


class QueryModel(BaseModel):
    def __init__(self, data: list[Query], parent: DefaultBaseType | None = None):
        super().__init__(data, parent)


class User(DefaultBaseType):
    """None."""

    def __init__(
        self,
        parent: QObject = None,
        name: str = None,
        age: int = None,
        agePoint: float = None,
        male: bool = None,
        id: str = None,
    ):
        super().__init__(parent)
        self._name = name
        self._age = age
        self._agePoint = agePoint
        self._male = male
        self._id = id

    @classmethod
    def from_dict(cls, parent, data: dict) -> User:
        return cls(
            parent=parent,
            name=data.get("name", None),
            age=data.get("age", None),
            agePoint=data.get("agePoint", None),
            male=data.get("male", None),
            id=data.get("id", None),
        )

    nameChanged = Signal()

    def name_setter(self, v: str) -> None:
        self._name = v
        self.nameChanged.emit()

    @qproperty(type=str, fset=name_setter, notify=nameChanged)
    def name(self):
        return self._name

    ageChanged = Signal()

    def age_setter(self, v: int) -> None:
        self._age = v
        self.ageChanged.emit()

    @qproperty(type=int, fset=age_setter, notify=ageChanged)
    def age(self):
        return self._age

    agePointChanged = Signal()

    def agePoint_setter(self, v: float) -> None:
        self._agePoint = v
        self.agePointChanged.emit()

    @qproperty(type=float, fset=agePoint_setter, notify=agePointChanged)
    def agePoint(self):
        return self._agePoint

    maleChanged = Signal()

    def male_setter(self, v: bool) -> None:
        self._male = v
        self.maleChanged.emit()

    @qproperty(type=bool, fset=male_setter, notify=maleChanged)
    def male(self):
        return self._male

    idChanged = Signal()

    def id_setter(self, v: str) -> None:
        self._id = v
        self.idChanged.emit()

    @qproperty(type=str, fset=id_setter, notify=idChanged)
    def id(self):
        return self._id


class UserModel(BaseModel):
    def __init__(self, data: list[User], parent: DefaultBaseType | None = None):
        super().__init__(data, parent)


if __name__ == "__main__":
    print(2)
