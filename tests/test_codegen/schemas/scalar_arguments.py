from __future__ import annotations

from typing import TYPE_CHECKING

import strawberry

from tests.test_codegen.schemas.node_interface import NODE_DB, Node

if TYPE_CHECKING:
    from uuid import UUID


@strawberry.type()
class ScalarContainer(Node):
    string: str
    i: int
    f: float
    b: bool
    uuid: UUID


@strawberry.type
class Query:
    @strawberry.field()
    @staticmethod
    def get_container(
        string: str,
        i: int,
        f: float,
        b: bool,
        uuid: UUID,
    ) -> ScalarContainer:
        return ScalarContainer(
            string=string,
            i=i,
            f=f,
            b=b,
            uuid=uuid,
        )


@strawberry.type()
class Mutation:
    @strawberry.field()
    def modify_container(
        self,
        container_id: strawberry.ID,
        string: str,
        i: int,
        f: float,
        b: bool,
        uuid: UUID,
    ) -> ScalarContainer:
        container: ScalarContainer = NODE_DB.get(container_id)
        container.string = string
        container.i = i
        container.f = f
        container.b = b
        container.uuid = uuid
        return container


schema = strawberry.Schema(query=Query)
