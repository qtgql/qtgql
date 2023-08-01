from __future__ import annotations

import strawberry

from tests.conftest import factory
from tests.test_codegen.schemas.node_interface import NODE_DB, Node


def create_tags() -> list[str]:
    return [factory.text.word() for _ in range(7)]


@strawberry.type
class Post(Node):
    content: str = strawberry.field(default_factory=factory.text.quote)
    tags: list[str] = strawberry.field(default_factory=create_tags)


@strawberry.type
class Query:
    @strawberry.field
    def post(self) -> Post:
        return Post()


@strawberry.type()
class Mutation:
    @strawberry.field
    def add_tag(self, post_id: strawberry.ID, tag: str) -> Post:
        post: Post = NODE_DB.get(post_id)
        post.tags.append(tag)
        return post


schema = strawberry.Schema(query=Query, mutation=Mutation)
