from attrs import define


@define
class CustomScalarDefinition:
    type_name: str
    graphql_name: str
    raw_type: str
    deserialized_type: str
    property_type: str
    include_path: str


# An ISO-8601 encoded datetime.
DateTimeScalar = CustomScalarDefinition(
    type_name="DateTimeScalar",
    graphql_name="DateTime",
    raw_type="QString",
    deserialized_type="QDateTime",
    property_type="QString",
    include_path="<qtgqlcustomscalars.hpp>",
)

# An ISO-8601 encoded date.
#
# class DateScalar(BaseCustomScalar[date, str]):
#     """An ISO-8601 encoded date."""
#
#
#     def parse_value(self) -> str:
#
#     @classmethod
#     def deserialize(cls, v=None) -> "DateScalar":
#         if v:
#
#     def to_qt(self) -> str:
#
#
# class TimeScalar(BaseCustomScalar[time, str]):
#     """an ISO-8601 encoded time."""
#
#
#     def parse_value(self) -> str:
#
#     @classmethod
#     def deserialize(cls, v: Optional[str] = None) -> "TimeScalar":
#         if v:
#
#     def to_qt(self) -> str:
#
#
# class DecimalScalar(BaseCustomScalar[Decimal, str]):
#     """A Decimal value serialized as a string."""
#
#
#     def parse_value(self) -> str:
#
#     @classmethod
#     def deserialize(cls, v: Optional[str] = None) -> "DecimalScalar":
#         if v:
#
#     def to_qt(self) -> str:


CustomScalarMap = dict[str, CustomScalarDefinition]
CUSTOM_SCALARS: CustomScalarMap = {
    DateTimeScalar.graphql_name: DateTimeScalar,
}
