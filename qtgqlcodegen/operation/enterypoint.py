from __future__ import annotations

from typing import TYPE_CHECKING

from qtgqlcodegen.operation.evaluation import evaluate_operation
from qtgqlcodegen.operation.visitors import (
    FragmentsVisitor,
    FragSpreadUnzipper,
    OperationsMapper,
    UsedFragmentFinder,
)

if TYPE_CHECKING:
    import graphql

    from qtgqlcodegen.operation.definitions import QtGqlFragmentDefinition, QtGqlOperationDefinition
    from qtgqlcodegen.schema.definitions import SchemaTypeInfo


def evaluate_operations(
    operations_document: graphql.DocumentNode,
    type_info: SchemaTypeInfo,
) -> dict[str, QtGqlOperationDefinition]:
    fragments = FragmentsVisitor.get_fragments(operations_document)
    evaluated_operations: list[QtGqlOperationDefinition] = []

    operations = OperationsMapper.evaluate(
        type_info,
        operations_document,
    )

    if fragments:
        unzipped_doc = FragSpreadUnzipper.unzip_doc(operations_document, fragments)
        unzipped_operations = OperationsMapper.evaluate(type_info, unzipped_doc)
    else:
        unzipped_operations = operations

    for i in range(len(operations)):
        used_fragments: tuple[QtGqlFragmentDefinition, ...] = ()
        if fragments:
            used_fragments = UsedFragmentFinder.get_used_fragments(
                available_fragments=fragments,
                operation=operations[i],
            )
        evaluated_operations.append(
            evaluate_operation(
                real_operation=operations[i],
                unzipped_operation=unzipped_operations[i],
                schema_type_info=type_info,
                used_fragments=used_fragments,
            ),
        )

    return {op.name: op for op in evaluated_operations}
