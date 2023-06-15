from __future__ import annotations

import enum
from datetime import datetime, timezone

import strawberry
from tests.conftest import fake
from tests.test_codegen.schemas.node_interface import NODE_DB, Node


@strawberry.enum
class SampleEnum(enum.Enum):
    A, B, C = range(3)


@strawberry.type
class Post(Node):
    header: str = strawberry.field(default_factory=fake.paragraph)
    content: str = strawberry.field(default_factory=fake.paragraph)
    createdAt: datetime = strawberry.field(default_factory=lambda: fake.date_time(timezone.utc))
    comments: list[Comment] = strawberry.field(default_factory=list)


@strawberry.type()
class Comment(Node):
    content: str = strawberry.field(default_factory=fake.paragraph)
    commenter: str = strawberry.field(default_factory=fake.first_name)


@strawberry.type
class Query:
    @strawberry.field
    def post(self) -> Post:
        return Post(comments=[Comment() for _ in range(5)])

    @strawberry.field()
    def get_post_by_id(self, id: strawberry.ID) -> Post:
        return NODE_DB.get(id)

    @strawberry.field
    def get_enum_name(self, enum_input: SampleEnum) -> str:
        return enum_input.name


@strawberry.input()
class CreatePostInput:
    content: str
    header: str


@strawberry.type
class Mutation:
    @strawberry.mutation
    def changePostHeader(self, post_id: strawberry.ID, new_header: str) -> Post:
        post: Post = NODE_DB.get(post_id)
        post.header = new_header
        return post

    @strawberry.mutation
    def createPost(self, input: CreatePostInput) -> Post:
        return Post(content=input.content, header=input.header)


schema = strawberry.Schema(query=Query, mutation=Mutation)

if __name__ == "__main__":
    ...
