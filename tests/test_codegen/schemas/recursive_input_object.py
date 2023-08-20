from __future__ import annotations

import strawberry


@strawberry.input()
class RecursiveInput:
    inp: RecursiveInput | None = None
    level: int = 0


@strawberry.type
class Query:
    @strawberry.field()
    def foobar(self, inp: RecursiveInput) -> int:
        if inp.inp:
            return inp.inp.level
        return inp.level


schema = strawberry.Schema(query=Query)
