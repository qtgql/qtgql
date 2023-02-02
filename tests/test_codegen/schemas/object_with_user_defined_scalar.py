import strawberry

countrymap = {"isr": "Israel", "uk": "United Kingdom"}


@strawberry.scalar(
    name="CountryScalar",
    description="countries by codename",
    serialize=lambda v: countrymap[v],
    parse_value=lambda v: v,
)
class CountryScalar:
    ...


@strawberry.type
class User:
    name: str
    age: int
    country: CountryScalar


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name="Patrick", age=100, country="isr")


schema = strawberry.Schema(query=Query)
