from __future__ import annotations

from typing import Optional, TypeVar

from PySide6.QtCore import QAbstractListModel, QByteArray, QObject, Qt

from qtgql import slot

__all__ = ["BaseModel", "get_base_graphql_object"]


class _BaseQGraphQLObject(QObject):
    type_map: dict[str, type[_BaseQGraphQLObject]]

    def __init_subclass__(cls, **kwargs):
        cls.type_map[cls.__name__] = cls

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

    @classmethod
    def from_dict(
        cls, parent: T_BaseQGraphQLObject, data: dict
    ) -> T_BaseQGraphQLObject:  # pragma: no cover
        raise NotImplementedError

    @classmethod
    def deserialize_optional_child(
        cls,
        parent: Optional[T_BaseQGraphQLObject],
        data: dict,
        child: type[T_BaseQGraphQLObject],
        field_name: str,
    ) -> Optional[T_BaseQGraphQLObject]:
        if found := data.get(field_name, None):
            return child.from_dict(parent, found)  # type: ignore

    @classmethod
    def deserialize_list_of(
        cls,
        parent: Optional[T_BaseQGraphQLObject],
        data: dict,
        model: type[T_BaseModel],
        field_name: str,
        of_type: type[T_BaseQGraphQLObject],
    ) -> Optional[T_BaseModel]:
        if found := data.get(field_name, None):
            return model(parent=parent, data=[of_type.from_dict(parent, data) for data in found])  # type: ignore

    @classmethod
    def deserialize_union(
        cls,
        parent: Optional[T_BaseQGraphQLObject],
        data: dict,
        field_name: str,
    ) -> Optional[T_BaseModel]:
        if found := data.get(field_name, None):
            child = cls.type_map[found["__typename"]]
            return child.from_dict(parent, found)  # type: ignore


class BaseModel(QAbstractListModel):
    OBJECT_ROLE = Qt.ItemDataRole.UserRole + 1

    def __init__(self, data: list[T_BaseQGraphQLObject], parent: Optional[QObject] = None):
        super().__init__(parent)
        self._data = data

    def rowCount(self, *args, **kwargs) -> int:
        return len(self._data)

    def roleNames(self) -> dict:
        return {self.OBJECT_ROLE: QByteArray("object")}  # type: ignore

    def data(self, index, role=...) -> Optional[T_BaseQGraphQLObject]:
        if index.row() < len(self._data) and index.isValid():
            if role == self.OBJECT_ROLE:
                return self._data[index.row()]
            raise NotImplementedError(
                f"role {role} is not a valid role for {self.__class__.__name__}"
            )

    def append(self, node: T_BaseQGraphQLObject) -> None:
        count = self.rowCount()
        self.beginInsertRows(self.index(count), count, count)
        self._data.append(node)
        self.endInsertRows()

    @slot
    def pop(self, index: Optional[int] = None) -> None:
        index = -1 if index is None else index
        real_index = index if index > -1 else self.rowCount()
        self.beginRemoveRows(self.index(index - 1).parent(), real_index, real_index)
        self._data.pop(index)
        self.endRemoveRows()


def get_base_graphql_object(name: str) -> type[_BaseQGraphQLObject]:
    """
    :param name: valid attribute name (used by codegen to import it).
    :returns: A type to be extended by all generated types.
    """
    type_map: dict[str, type[_BaseQGraphQLObject]] = {}
    return type(name, (_BaseQGraphQLObject,), {"type_map": type_map})  # type: ignore


BaseGraphQLObject = get_base_graphql_object("BaseGraphQLObject")

T_BaseModel = TypeVar("T_BaseModel", bound=BaseModel)
T_BaseQGraphQLObject = TypeVar("T_BaseQGraphQLObject", bound=_BaseQGraphQLObject)
