from __future__ import annotations

import uuid
from typing import TypeVar

import strawberry


@strawberry.interface
class Node:
    id: strawberry.ID = strawberry.field(default_factory=lambda: uuid.uuid4().hex)

    def __init_subclass__(cls, **kwargs):
        cls.__hash__ = cls.hash_impl  # because of https://stackoverflow.com/a/53519136/16776498
        setattr(cls, f"_{cls.__name__}__typename", cls.__name__)

    def __post_init__(self):
        NODE_DB.insert(self)

    def hash_impl(self) -> int:
        return hash(self.id)

    def __hash__(self) -> int:
        return self.hash_impl()


T_Node = TypeVar("T_Node", bound=Node)


class NodeDb:
    def __init__(self):
        self._data = {}

    def insert(self, node: T_Node) -> T_Node:
        self._data[node.id] = node

    def get(self, id: str, strict: bool = True) -> Node | None:
        ret = self._data.get(id, None)
        if not ret and strict:
            raise KeyError(f"{id} not exists in the nodes store")
        return ret


NODE_DB = NodeDb()
