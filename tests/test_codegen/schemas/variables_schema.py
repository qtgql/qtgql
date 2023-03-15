from __future__ import annotations

from datetime import datetime, timezone

import strawberry

from tests.conftest import fake
from tests.test_codegen.schemas.node_interface import NODE_DB, Node


@strawberry.type
class Post(Node):
    comments: list[Comment]
    createdAt: datetime = strawberry.field(default_factory=lambda: fake.date_time(timezone.utc))
    header: str = strawberry.field(default_factory=fake.paragraph)


@strawberry.type()
class Comment(Node):
    content: str = strawberry.field(default_factory=fake.paragraph)
    commenter: str = strawberry.field(default_factory=fake.first_name)


@strawberry.type
class Query:
    @strawberry.field
    def post(self) -> Post:
        return Post(comments=[Comment() for _ in range(5)])


@strawberry.type
class Mutation:
    @strawberry.field
    def changePostHeader(self, post_id: strawberry.ID, new_header: str) -> Post:
        post: Post = NODE_DB.get(post_id)
        post.header = new_header
        return post


schema = strawberry.Schema(query=Query, mutation=Mutation)

if __name__ == "__main__":
    ...
