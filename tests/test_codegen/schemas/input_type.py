from __future__ import annotations

import strawberry
from tests.conftest import fake
from tests.test_codegen.schemas.node_interface import NODE_DB, Node


@strawberry.type
class Post(Node):
    header: str = strawberry.field(default_factory=fake.paragraph)
    content: str = strawberry.field(default_factory=fake.paragraph)


@strawberry.type
class Query:
    @strawberry.field()
    def foo(self) -> None:
        return


@strawberry.input()
class CreatePostInput:
    content: str
    header: str


@strawberry.input()
class ModifyPostContentInput:
    post_id: strawberry.ID
    new_content: str


@strawberry.type
class Mutation:
    @strawberry.mutation
    def createPost(self, input: CreatePostInput) -> Post:
        return Post(content=input.content, header=input.header)

    @strawberry.field
    def modify_post_content(self, input_: ModifyPostContentInput) -> Post:
        post: Post = NODE_DB.get(input_.post_id)
        post.content = input_.new_content
        return post


schema = strawberry.Schema(query=Query, mutation=Mutation)

if __name__ == "__main__":
    ...
