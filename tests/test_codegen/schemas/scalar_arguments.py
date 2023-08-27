from __future__ import annotations

import dataclasses
import uuid
from typing import TYPE_CHECKING
from uuid import UUID

import strawberry

from tests.conftest import factory
from tests.test_codegen.schemas.node_interface import NODE_DB, Node

if TYPE_CHECKING:
    from strawberry.types import Info


@strawberry.type()
class ScalarContainer(Node):
    string: str = strawberry.field(default_factory=factory.text.color)
    i: int = strawberry.field(default_factory=lambda: factory.develop.random.randint(0, 123524))
    f: float = strawberry.field(
        default_factory=lambda: factory.develop.random.randint(0, 12356) + 0.1243,
    )
    b: bool = False
    uuid: UUID = strawberry.field(
        default_factory=uuid.uuid4,
        description="This would be the id of the object",
    )


@strawberry.type
class Query:
    @strawberry.field()
    @staticmethod
    def get_container(
        info: Info,
        string: str,
        i: int,
        f: float,
        b: bool,
        uuid: UUID,
    ) -> ScalarContainer:
        if node_id := info.context["request"].headers.get("NODE_ID", None):
            container: ScalarContainer = NODE_DB.get(node_id)
            prev_bool = container.b
            scramble = ScalarContainer()
            replace_dict = strawberry.asdict(scramble)
            replace_dict.pop("id")
            ret = dataclasses.replace(container, **replace_dict)
            ret.b = not prev_bool
            return ret

        return ScalarContainer(
            string=string,
            i=i,
            f=f,
            b=b,
            uuid=uuid,
        )


schema = strawberry.Schema(query=Query)
