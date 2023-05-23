from attrs import define


@define
class CustomScalarDefinition:
    type_name: str
    graphql_name: str
    deserialized_type: str
    property_type: str
    include_path: str


# An ISO-8601 encoded datetime.
DateTimeScalarDefinition = CustomScalarDefinition(
    type_name="qtgql::DateTimeScalar",
    graphql_name="DateTime",
    deserialized_type="QDateTime",
    property_type="QString",
    include_path="<qtgql/customscalars/customscalars.hpp>",
)
DateScalarDefinition = CustomScalarDefinition(
    type_name="qtgql::DateScalar",
    graphql_name="Date",
    deserialized_type="QString",
    property_type="QString",
    include_path="<qtgql/customscalars/customscalars.hpp>",
)
DecimalScalarDefinition = CustomScalarDefinition(
    type_name="qtgql::DecimalScalar",
    graphql_name="Decimal",
    deserialized_type="QString",
    property_type="QString",
    include_path="<qtgql/customscalars/customscalars.hpp>",
)


CustomScalarMap = dict[str, CustomScalarDefinition]
CUSTOM_SCALARS: CustomScalarMap = {
    DateTimeScalarDefinition.graphql_name: DateTimeScalarDefinition,
    DecimalScalarDefinition.graphql_name: DecimalScalarDefinition,
    DateScalarDefinition.graphql_name: DateScalarDefinition,
}
