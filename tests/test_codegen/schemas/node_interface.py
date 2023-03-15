from __future__ import annotations

import uuid
from typing import TypeVar

import strawberry


@strawberry.interface
class Node:
    id: strawberry.ID = strawberry.field(default_factory=lambda: uuid.uuid4().hex)


T_Node = TypeVar("T_Node", bound=Node)


class NodeDb:
    def __init__(self):
        self._data = {}

    def insert(self, node: T_Node) -> T_Node:
        self._data[node.id] = node

    def get(self, id: str) -> Node | None:
        return self._data.get(id, None)


NODE_DB = NodeDb()
