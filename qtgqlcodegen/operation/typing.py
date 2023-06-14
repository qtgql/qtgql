from __future__ import annotations

from typing import TYPE_CHECKING

import attrs

if TYPE_CHECKING:
    from qtgqlcodegen.operation.definitions import QtGqlQueriedObjectType
    from qtgqlcodegen.schema.definitions import QtGqlVariableDefinition
    from qtgqlcodegen.schema.typing import SchemaTypeInfo


@attrs.define(slots=False)
class OperationTypeInfo:
    schema_type_info: SchemaTypeInfo
    narrowed_types: tuple[QtGqlQueriedObjectType, ...] = attrs.Factory(dict)
    variables: list[QtGqlVariableDefinition] = attrs.Factory(list)
