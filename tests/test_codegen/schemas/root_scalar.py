from __future__ import annotations

import strawberry
from tests.conftest import factory


@strawberry.type
class Query:
    @strawberry.field
    @staticmethod
    def name(self) -> str:
        return factory.person.name()


schema = strawberry.Schema(query=Query)
