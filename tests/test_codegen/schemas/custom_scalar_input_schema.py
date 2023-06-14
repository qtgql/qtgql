from datetime import date, datetime, time
from decimal import Decimal

import strawberry


@strawberry.input()
class SupportedCustomScalarsInput:
    dt: datetime
    date_: date
    time_: time
    decimal: Decimal


@strawberry.type()
class Container:
    dt: datetime
    date_: date
    time_: time
    decimal: Decimal


@strawberry.type
class Query:
    @strawberry.field
    def echo_custom_scalar(
        self,
        dt: datetime,
        date_: date,
        time_: time,
        decimal: Decimal,
    ) -> Container:
        return Container(dt=dt, date_=date_, time_=time_, decimal=decimal)

    @strawberry.field()
    def echo_custom_scalar_input_obj(self, input: SupportedCustomScalarsInput) -> Container:
        return Container(dt=input.dt, date_=input.date_, time_=input.time_, decimal=input.decimal)


schema = strawberry.Schema(query=Query)
