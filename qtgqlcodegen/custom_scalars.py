from qtgqlcodegen.schema.typing import CustomScalarDefinition
from qtgqlcodegen.schema.definitions import CustomScalarMap

# An ISO-8601 encoded datetime.
DateTimeScalarDefinition = CustomScalarDefinition(
    type_name="qtgql::customscalars::DateTimeScalar",
    graphql_name="DateTime",
    deserialized_type="QDateTime",
    type_for_proxy="QString",
    include_path="<qtgql/customscalars/customscalars.hpp>",
)
DateScalarDefinition = CustomScalarDefinition(
    type_name="qtgql::customscalars::DateScalar",
    graphql_name="Date",
    deserialized_type="QDate",
    type_for_proxy="QString",
    include_path="<qtgql/customscalars/customscalars.hpp>",
)
TimeScalarDefinition = CustomScalarDefinition(
    type_name="qtgql::customscalars::TimeScalar",
    graphql_name="Time",
    deserialized_type="QTime",
    type_for_proxy="QString",
    include_path="<qtgql/customscalars/customscalars.hpp>",
)

DecimalScalarDefinition = CustomScalarDefinition(
    type_name="qtgql::customscalars::DecimalScalar",
    graphql_name="Decimal",
    deserialized_type="QString",
    type_for_proxy="QString",
    include_path="<qtgql/customscalars/customscalars.hpp>",
)

CUSTOM_SCALARS: CustomScalarMap = {
    DateTimeScalarDefinition.graphql_name: DateTimeScalarDefinition,
    DateScalarDefinition.graphql_name: DateScalarDefinition,
    TimeScalarDefinition.graphql_name: TimeScalarDefinition,
    DecimalScalarDefinition.graphql_name: DecimalScalarDefinition,
}
