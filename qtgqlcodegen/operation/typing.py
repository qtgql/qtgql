from __future__ import annotations

from typing import TYPE_CHECKING

import attrs

if TYPE_CHECKING:
    from qtgqlcodegen.operation.definitions import QtGqlQueriedObjectType
    from qtgqlcodegen.schema.definitions import QtGqlVariableDefinition, SchemaTypeInfo


@attrs.define(slots=False)
class OperationTypeInfo:
    schema_type_info: SchemaTypeInfo
    narrowed_types_map: dict[str, QtGqlQueriedObjectType] = attrs.Factory(dict)
    variables: list[QtGqlVariableDefinition] = attrs.Factory(list)

    def narrowed_types(self) -> tuple[QtGqlQueriedObjectType, ...]:
        return tuple(self.narrowed_types_map.values())
