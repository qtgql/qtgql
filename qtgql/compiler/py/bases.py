from __future__ import annotations

from typing import TypeVar

from PySide6.QtCore import QObject, Qt

from qtgql import slot


class BaseQGraphQLObject(QObject):
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

    def from_dict(self, parent: BaseQGraphQLObject, data: dict) -> BaseQGraphQLObject:
        raise NotImplementedError

    @classmethod
    def deserialize_optional_child(
        cls,
        parent: T_BaseQGraphQLObject,
        data: dict,
        child: type[T_BaseQGraphQLObject],
        field_name: str,
    ) -> None | (T_BaseQGraphQLObject):
        if found := data.get(field_name, None):
            return child.from_dict(parent, found)
        return None

    @classmethod
    def deserialize_list_of(
        cls,
        parent: T_BaseQGraphQLObject,
        data: dict,
        model: type[T_BaseModel],
        field_name: str,
        of_type: type[T_BaseQGraphQLObject],
    ) -> T_BaseModel | None:
        if found := data.get(field_name, None):
            return model(parent=parent, data=[of_type.from_dict(parent, data) for data in found])
        return None


class BaseModel(QObject):
    PROPERTY_ROLE = Qt.ItemDataRole.UserRole + 1

    def __init__(self, data: list[BaseQGraphQLObject], parent: QObject | None = None):
        super().__init__(parent)
        self._data = data

    def flags(self, index):
        if index.row() < len(self._data) and index.isValid():
            return Qt.ItemFlag.ItemIsEditable
        return Qt.ItemFlag.NoItemFlags

    def roleNames(self) -> dict:
        return {b"object": self.PROPERTY_ROLE}

    def data(self, index, role=...) -> BaseQGraphQLObject | None:
        if index.row() < len(self._data) and index.isValid():
            if role == self.PROPERTY_ROLE:
                return self._data[index.row()]
            raise NotImplementedError(
                f"role {role} is not a valid role for {self.__class__.__name__}"
            )

    def append(self, node: BaseQGraphQLObject) -> None:
        count = self.rowCount()
        self.beginInsertRows(self.index(count), count, count)
        self._data.append(node)
        self.endInsertRows()

    @slot
    def pop(self, index: int | None = None) -> None:
        index = -1 if index is None else index
        real_index = index if index > -1 else self.rowCount()
        self.beginRemoveRows(self.index(index - 1).parent(), real_index, real_index)
        self._data.pop(index)
        self.endRemoveRows()


T_BaseModel = TypeVar("T_BaseModel", bound=BaseModel)
T_BaseQGraphQLObject = TypeVar("T_BaseQGraphQLObject", bound=BaseQGraphQLObject)