from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

import graphql
from frozendict import frozendict
from graphql import OperationDefinitionNode, OperationType, language as gql_lang
from graphql.language import visitor
from typingref import UNSET

from qtgqlcodegen.core.graphql_ref import (
    has_id_selection,
    has_typename_selection,
    inject_id_selection,
    inject_typename_selection,
    is_field_node,
    is_inline_fragment,
    is_operation_def_node,
)
from qtgqlcodegen.operation.definitions import (
    QtGqlOperationDefinition,
    QtGqlQueriedField,
    QtGqlQueriedObjectType,
)
from qtgqlcodegen.operation.typing import OperationTypeInfo
from qtgqlcodegen.schema.evaluation import evaluate_variable
from qtgqlcodegen.utils import require

if TYPE_CHECKING:
    from qtgqlcodegen.schema.definitions import QtGqlFieldDefinition, SchemaTypeInfo
    from qtgqlcodegen.schema.typing import QtGqlObjectTypeDefinition


def is_type_name_selection(field_node: gql_lang.FieldNode):
    # typename is not a 'real' selection and is handled with special care.
    if field_node.name.value == "__typename":
        return True
    return False


def get_operation_root_field_name(operation_node: gql_lang.OperationDefinitionNode) -> str:
    return operation_node.selection_set.selections[0].name.value  # type: ignore


def _evaluate_field_from_node(
    field_node: gql_lang.FieldNode,
    field_type: QtGqlObjectTypeDefinition,
    type_info: OperationTypeInfo,
    parent_interface_field: QtGqlQueriedField | None = UNSET,
) -> QtGqlQueriedField:
    return _evaluate_field(
        type_info=type_info,
        field_definition=field_type.fields_dict[field_node.name.value],
        selection_set=field_node.selection_set,
        parent_interface_field=parent_interface_field,
    )


def _evaluate_field(
    type_info: OperationTypeInfo,
    field_definition: QtGqlFieldDefinition,
    selection_set: gql_lang.SelectionSetNode | None,
    parent_interface_field: QtGqlQueriedField | None = UNSET,
    is_root: bool = False,
) -> QtGqlQueriedField:
    """Main purpose here is to find inner selections of fields, this could be
    an object type, interface, union or a list.

    Any other fields should not have inner selections.
    """
    assert parent_interface_field is not UNSET
    if not hasattr(selection_set, "selections"):
        return QtGqlQueriedField(definition=field_definition, type_info=type_info, is_root=is_root)
    assert selection_set
    tp = field_definition.type
    if tp.is_model:  # GraphQL's lists are basically the object beneath them in terms of selections.
        tp = tp.is_model

    tp_is_union = tp.is_union

    # inject id selection for types that supports it. unions are handled below.
    if field_definition.can_select_id and not has_id_selection(selection_set):
        inject_id_selection(selection_set)

    selections: dict[str, QtGqlQueriedField] = {}
    choices: defaultdict[str, dict[str, QtGqlQueriedField]] = defaultdict(dict)
    narrowed_type: QtGqlQueriedObjectType | None = None
    # inject parent interface selections.
    if (tp.is_object_type or tp.is_interface) and parent_interface_field:
        selections.update({f.name: f for f in parent_interface_field.selections.values()})

    if tp_is_union:
        for selection in selection_set.selections:
            fragment = is_inline_fragment(selection)
            assert fragment

            type_name = fragment.type_condition.name.value
            concrete = type_info.schema_type_info.get_object_type(type_name)
            assert concrete
            if not has_typename_selection(fragment.selection_set):
                inject_typename_selection(fragment.selection_set)
            if not has_id_selection(fragment.selection_set) and concrete.implements_node:
                inject_id_selection(fragment.selection_set)

            for selection_node in fragment.selection_set.selections:
                field_node = is_field_node(selection_node)
                assert field_node

                if not is_type_name_selection(field_node):
                    __f = _evaluate_field_from_node(
                        field_node,
                        concrete,
                        type_info,
                        parent_interface_field,
                    )
                    choices[type_name][field_definition.name] = __f

    elif interface_def := tp.is_interface:
        # first get all linear selections.
        for selection in selection_set.selections:
            if not is_inline_fragment(selection):
                field_node = is_field_node(selection)
                assert field_node
                if not is_type_name_selection(field_node):
                    __f = _evaluate_field_from_node(
                        field_node,
                        interface_def,
                        type_info,
                        parent_interface_field,
                    )
                    selections[__f.name] = __f

        for selection in selection_set.selections:
            if inline_frag := is_inline_fragment(selection):
                type_name = inline_frag.type_condition.name.value
                # no need to validate inner types are implementation, graphql-core does this.
                concrete = type_info.schema_type_info.get_object_type(
                    type_name,
                ) or type_info.schema_type_info.get_interface_by_name(type_name)
                assert concrete
                for inner_selection in inline_frag.selection_set.selections:
                    field_node = is_field_node(inner_selection)
                    assert field_node
                    if not is_type_name_selection(field_node):
                        __f = _evaluate_field_from_node(
                            field_node,
                            concrete,
                            type_info,
                            parent_interface_field,
                        )
                        choices[type_name][field_definition.name] = __f

    else:  # object types.
        obj_def = tp.is_object_type
        assert obj_def
        for selection in selection_set.selections:
            field_node = is_field_node(selection)
            assert field_node
            if not is_type_name_selection(field_node):
                __f = _evaluate_field_from_node(
                    field_node,
                    obj_def,
                    type_info,
                    parent_interface_field,
                )
                selections[__f.name] = __f
        queried_obj = QtGqlQueriedObjectType(
            definition=obj_def,
            fields_dict=selections,
        )
        type_info.narrowed_types[queried_obj.name] = queried_obj
        narrowed_type = queried_obj

    def sorted_distinct_fields(
        fields: dict[str, QtGqlQueriedField],
    ) -> dict[str, QtGqlQueriedField]:
        return dict(sorted(fields.items()))

    return QtGqlQueriedField(
        definition=field_definition,
        selections=sorted_distinct_fields(selections),
        choices=frozendict({k: sorted_distinct_fields(v) for k, v in choices.items()}),
        type_info=type_info,
        narrowed_type=narrowed_type,
        is_root=is_root,
    )


def _evaluate_operation(
    operation: OperationDefinitionNode,
    schema_type_info: SchemaTypeInfo,
) -> QtGqlOperationDefinition:
    type_info = OperationTypeInfo(schema_type_info)

    # input variables
    if variables_def := operation.variable_definitions:
        for var in variables_def:
            type_info.variables.append(evaluate_variable(type_info.schema_type_info, var))

    root_field_def = require(is_field_node(operation.selection_set.selections[0]))
    root_type = require(type_info.schema_type_info.get_object_type(operation.operation.name))
    root_field = _evaluate_field(
        type_info,
        root_type.fields_dict[get_operation_root_field_name(operation)],
        root_field_def.selection_set,
        parent_interface_field=None,
        is_root=True,
    )
    return QtGqlOperationDefinition(
        root_field=root_field,
        operation_def=operation,
        variables=type_info.variables,
    )


class _OperationsVisitor(visitor.Visitor):
    def __init__(self, type_info: SchemaTypeInfo):
        super().__init__()
        self.schema_type_info = type_info
        self.operations: dict[str, QtGqlOperationDefinition] = {}

    def enter_operation_definition(self, node, key, parent, path, ancestors) -> None:
        if operation := is_operation_def_node(node):
            if operation.operation in (
                OperationType.QUERY,
                OperationType.MUTATION,
                OperationType.SUBSCRIPTION,
            ):
                assert operation.name, "QtGql enforces operations to have names."
                self.operations[operation.name.value] = _evaluate_operation(
                    operation,
                    self.schema_type_info,
                )


def evaluate_operations(
    operations_document: graphql.DocumentNode,
    type_info: SchemaTypeInfo,
) -> dict[str, QtGqlOperationDefinition]:
    operation_visitor = _OperationsVisitor(type_info)
    graphql.visit(operations_document, operation_visitor)
    assert operation_visitor.operations
    return operation_visitor.operations
