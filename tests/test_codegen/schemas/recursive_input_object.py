from __future__ import annotations

import strawberry


@strawberry.input()
class RecursiveInput:
    inp: RecursiveInput | None = None
    depth: int = 0


@strawberry.type
class Query:
    @strawberry.field()
    def depth(self, inp: RecursiveInput) -> int:
        if inp.inp:
            return inp.inp.depth
        return inp.depth


schema = strawberry.Schema(query=Query)
