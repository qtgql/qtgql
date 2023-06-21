from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

import graphql
from graphql import OperationDefinitionNode, OperationType, language as gql_lang
from graphql.language import visitor

from qtgqlcodegen.core.graphql_ref import (
    has_id_selection,
    has_typename_selection,
    inject_id_selection,
    inject_typename_selection,
    is_field_node,
    is_inline_fragment,
    is_named_type_node,
    is_nonnull_node,
    is_operation_def_node,
)
from qtgqlcodegen.operation.definitions import (
    OperationTypeInfo,
    QtGqlOperationDefinition,
    QtGqlQueriedField,
    QtGqlVariableUse,
)
from qtgqlcodegen.schema.definitions import (
    QtGqlFieldDefinition,
    QtGqlVariableDefinition,
    SchemaTypeInfo,
)
from qtgqlcodegen.schema.evaluation import evaluate_graphql_type
from qtgqlcodegen.types import (
    QtGqlInterface,
    QtGqlList,
    QtGqlOptional,
    QtGqlQueriedInterface,
    QtGqlQueriedObjectType,
    QtGqlQueriedUnion,
    QtGqlUnion,
)
from qtgqlcodegen.utils import require

if TYPE_CHECKING:
    from qtgqlcodegen.types import QtGqlObjectType, QtGqlTypeABC


def is_type_name_selection(field_node: gql_lang.FieldNode):
    # typename is not a 'real' selection and is handled with special care.
    if field_node.name.value == "__typename":
        return True
    return False


def _evaluate_variable_uses(
    type_info: OperationTypeInfo,
    field: QtGqlFieldDefinition,
    arguments: tuple[gql_lang.ArgumentNode, ...],
) -> list[QtGqlVariableUse]:
    ret: list[QtGqlVariableUse] = []
    for arg in arguments:
        index = field.index_for_argument(arg.name.value)
        var_name = arg.value.name.value  # type: ignore[attr-defined]
        for variable in type_info.variables:
            if var_name == variable.name:
                ret.append(
                    QtGqlVariableUse(argument=(index, field.arguments[index]), variable=variable),
                )
    assert len(ret) == len(arguments), "could not find all variable uses"
    return ret


def _evaluate_variable_node_type(
    type_info: SchemaTypeInfo,
    node: graphql.TypeNode,
) -> QtGqlTypeABC:
    if nonnull := is_nonnull_node(node):
        return evaluate_graphql_type(
            type_info,
            graphql.type.GraphQLNonNull(
                type_info.schema_definition.get_type(nonnull.type.name.value),  # type: ignore
            ),
        )

    if named_type := is_named_type_node(node):
        gql_concrete = type_info.schema_definition.get_type(named_type.name.value)
        assert gql_concrete
        return evaluate_graphql_type(type_info, gql_concrete)
    raise NotImplementedError(node, "Type is not supported as a variable ATM")


def _evaluate_variable(
    type_info: SchemaTypeInfo,
    var: gql_lang.VariableDefinitionNode,
) -> QtGqlVariableDefinition:
    return QtGqlVariableDefinition(
        name=var.variable.name.value,
        type=_evaluate_variable_node_type(type_info, var.type),
    )


def _evaluate_selection_set_type(
    type_info: OperationTypeInfo,
    concrete_type: QtGqlTypeABC,
    selection_set_node: gql_lang.SelectionSetNode | None,
    path: str,
) -> QtGqlTypeABC:
    ret: QtGqlTypeABC | None = None
    if not selection_set_node:
        # these types have no selections
        assert (
            concrete_type.is_builtin_scalar
            or concrete_type.is_custom_scalar
            or concrete_type.is_enum
        )
        ret = concrete_type  # currently there is no need for a "proxied" type.

    elif obj_type := concrete_type.is_object_type:
        ret = _evaluate_object_type(
            type_info=type_info,
            concrete=obj_type,
            selection_set=selection_set_node,
            path=path,
        )
    elif lst := concrete_type.is_model:
        ret = _evaluate_list(
            type_info=type_info,
            concrete=lst,
            selection_set=selection_set_node,
            path=path,
        )
    elif interface := concrete_type.is_interface:
        ret = _evaluate_interface(
            type_info=type_info,
            concrete=interface,
            selection_set=selection_set_node,
            path=path,
        )
    elif is_union := concrete_type.is_union:
        ret = _evaluate_union(
            type_info=type_info,
            concrete=is_union,
            selection_set=selection_set_node,
            path=path,
        )
    if not ret:  # pragma: no cover
        raise NotImplementedError(f"type {concrete_type} not supported yet")

    if concrete_type.is_optional:
        return QtGqlOptional(of_type=ret)
    return ret


def _evaluate_field(
    type_info: OperationTypeInfo,
    concrete_field: QtGqlFieldDefinition,
    field_node: gql_lang.FieldNode,
    path: str,
    origin: QtGqlObjectType,
) -> QtGqlQueriedField:
    path += concrete_field.name
    return QtGqlQueriedField(
        type=_evaluate_selection_set_type(
            type_info,
            concrete_field.type,
            field_node.selection_set,
            path,
        ),
        concrete=concrete_field,
        variable_uses=_evaluate_variable_uses(type_info, concrete_field, field_node.arguments),
        origin=origin,
        type_info=type_info,
    )


def _evaluate_list(
    type_info: OperationTypeInfo,
    concrete: QtGqlList,
    selection_set: gql_lang.SelectionSetNode,
    path: str,
) -> QtGqlList:
    return QtGqlList(
        of_type=_evaluate_selection_set_type(
            type_info,
            concrete_type=concrete.of_type,
            selection_set_node=selection_set,
            path=path,
        ),
    )


def _evaluate_union(
    type_info: OperationTypeInfo,
    concrete: QtGqlUnion,
    selection_set: gql_lang.SelectionSetNode,
    path: str,
) -> QtGqlQueriedUnion:
    choices: defaultdict[str, dict[str, QtGqlQueriedField]] = defaultdict(dict)
    for selection in selection_set.selections:
        fragment = is_inline_fragment(selection)
        assert fragment
        type_name = fragment.type_condition.name.value
        # unions support only object types http://spec.graphql.org/October2021/#sec-Unions
        resolved_type = require(concrete.get_by_name(type_name))
        if not has_typename_selection(fragment.selection_set):
            inject_typename_selection(fragment.selection_set)
        if not has_id_selection(fragment.selection_set) and resolved_type.implements_node:
            inject_id_selection(fragment.selection_set)

        for selection_node in fragment.selection_set.selections:
            inner_field_node = require(is_field_node(selection_node))
            if not is_type_name_selection(inner_field_node):
                concrete_field = resolved_type.fields_dict[inner_field_node.name.value]
                __f = _evaluate_field(
                    type_info=type_info,
                    concrete_field=concrete_field,
                    field_node=inner_field_node,
                    path=path,
                    origin=resolved_type,
                )
                choices[type_name][concrete_field.name] = __f

    return QtGqlQueriedUnion(
        concrete=concrete,
        choices=choices,
    )


def _evaluate_interface(
    type_info: OperationTypeInfo,
    concrete: QtGqlInterface,
    selection_set: gql_lang.SelectionSetNode,
    path: str,  # current path in the query tree.
) -> QtGqlQueriedInterface:
    # first get all linear selections.
    linear_fields: dict[str, QtGqlQueriedField] = {}
    choices: defaultdict[str, dict[str, QtGqlQueriedField]] = defaultdict(dict)

    for selection in selection_set.selections:
        if not is_inline_fragment(selection):
            inner_field_node = is_field_node(selection)
            assert inner_field_node
            if not is_type_name_selection(inner_field_node):
                __f = _evaluate_field(
                    type_info=type_info,
                    concrete_field=concrete.fields_dict[inner_field_node.name.value],
                    field_node=inner_field_node,
                    path=path,
                    origin=concrete,
                )
                linear_fields[__f.name] = __f

    # evaluate type conditions
    for selection in selection_set.selections:
        if inline_frag := is_inline_fragment(selection):
            type_name = inline_frag.type_condition.name.value
            # no need to validate inner types are implementation, graphql-core does this.
            resolved_type = type_info.schema_type_info.get_object_type(
                type_name,
            ) or type_info.schema_type_info.get_interface(type_name)
            assert resolved_type
            for inner_selection in inline_frag.selection_set.selections:
                inner_field_node = is_field_node(inner_selection)
                assert inner_field_node
                if not is_type_name_selection(inner_field_node):
                    __f = _evaluate_field(
                        type_info=type_info,
                        concrete_field=resolved_type.fields_dict[inner_field_node.name.value],
                        field_node=inner_field_node,
                        path=path,
                        origin=resolved_type,
                    )
                    choices[type_name][inner_field_node.name.value] = __f
    for choice in choices.values():
        choice.update(linear_fields)

    name = f"{concrete.name}__{path}"
    ret = QtGqlQueriedInterface(
        name=name,
        concrete=concrete,
        choices=choices,
        fields_dict=linear_fields,
    )
    type_info.narrowed_interfaces_map[name] = ret
    return ret


def _evaluate_object_type(
    type_info: OperationTypeInfo,
    concrete: QtGqlObjectType,
    selection_set: gql_lang.SelectionSetNode,
    path: str,  # current path in the query tree.
) -> QtGqlQueriedObjectType:
    # inject id selection for node implementors, it is required for caching purposes.
    if concrete.implements_node and not has_id_selection(selection_set):
        inject_id_selection(selection_set)

    fields: dict[str, QtGqlQueriedField] = {}
    for selection in selection_set.selections:
        if f_node := is_field_node(selection):
            concrete_field = concrete.fields_dict[f_node.name.value]
            fields[concrete_field.name] = _evaluate_field(
                type_info=type_info,
                concrete_field=concrete_field,
                field_node=f_node,
                path=path,
                origin=concrete,
            )

    name = f"{concrete.name}__{path}"
    if ret := type_info.narrowed_types_map.get(name, None):
        return ret

    ret = QtGqlQueriedObjectType(
        name=name,
        concrete=concrete,
        fields_dict=fields,
    )
    type_info.narrowed_types_map[name] = ret
    return ret


def _evaluate_operation(
    operation: OperationDefinitionNode,
    schema_type_info: SchemaTypeInfo,
) -> QtGqlOperationDefinition:
    """Each operation generates a whole new "proxy" schema. That schema will
    contain only the fields that are currently queried. The way we do that is
    creating a so-called "proxy objects".

    - Each proxy object mirrors a concrete object at schema level.
    - Each proxy object contains only the fields that was queried for this field in the tree.

    And because of that, one object type (at the concrete schema) might have many proxy objects.
    """
    type_info = OperationTypeInfo(schema_type_info)

    # input variables
    if variables_def := operation.variable_definitions:
        for var in variables_def:
            type_info.variables.append(_evaluate_variable(type_info.schema_type_info, var))

    selections = operation.selection_set
    root_type = type_info.schema_type_info.operation_types[operation.operation.value]
    assert root_type, f"Make sure you have {operation.operation.name} type defined in your schema"
    root_proxy_type = _evaluate_object_type(
        type_info=type_info,
        concrete=root_type,
        selection_set=selections,
        path="",
    )
    assert len(root_proxy_type.fields) == 1
    root_field = root_proxy_type.fields[0]
    return QtGqlOperationDefinition(
        root_field=root_field,
        root_type=root_proxy_type,
        operation_def=operation,
        variables=type_info.variables,
        narrowed_types=tuple(type_info.narrowed_types_map.values()),
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
