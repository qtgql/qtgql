from __future__ import annotations

import strawberry

from tests.conftest import factory
from tests.test_codegen.schemas.node_interface import Node


def create_tags() -> list[str]:
    return [factory.text.word() for _ in range(7)]


@strawberry.type
class Post(Node):
    content: str = strawberry.field(default_factory=factory.text.answer)
    tags: list[str] = strawberry.field(default_factory=create_tags)


@strawberry.type
class Query:
    @strawberry.field
    def post(self) -> Post:
        return Post()


schema = strawberry.Schema(query=Query)
