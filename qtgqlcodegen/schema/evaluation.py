from __future__ import annotations

import warnings
from typing import Optional, Union

import graphql
from graphql import OperationType, language as gql_lang
from graphql.type import definition as gql_def

from qtgqlcodegen.builtin_scalars import BuiltinScalars
from qtgqlcodegen.core.exceptions import QtGqlException
from qtgqlcodegen.core.graphql_ref import (
    is_enum_definition,
    is_input_definition,
    is_interface_definition,
    is_list_definition,
    is_non_null_definition,
    is_object_definition,
    is_scalar_definition,
    is_union_definition,
)
from qtgqlcodegen.schema.typing import CustomScalarMap, GqlTypeHinter, SchemaTypeInfo, QtGqlVariableDefinition, \
    QtGqlInputFieldDefinition, QtGqlFieldDefinition, QtGqlObjectTypeDefinition, QtGqlInterfaceDefinition, \
    QtGqlInputObjectTypeDefinition, EnumValue, QtGqlEnumDefinition
from qtgqlcodegen.utils import anti_forward_ref


def evaluate_input_type(
    type_info: SchemaTypeInfo,
    type_: gql_def.GraphQLInputObjectType,
) -> QtGqlInputObjectTypeDefinition:
    ret = type_info.input_objects.get(type_.name, None)
    if not ret:
        ret = QtGqlInputObjectTypeDefinition(
            name=type_.name,
            docstring=type_.description,
            fields_dict={
                name: _evaluate_input_field(name, field) for name, field in type_.fields.items()
            },
        )
        type_info.input_objects[ret.name] = ret
    return ret


def evaluate_field_type(
    type_info: SchemaTypeInfo,
    t: gql_def.GraphQLType,
) -> GqlTypeHinter:
    # even though every type in qtgql has a default constructor,
    # hence there is no "real" non-null values
    # we store it as optional for generating nullable checks only for what's required.
    ret = None
    is_optional = True
    if non_null := is_non_null_definition(t):
        t = non_null.of_type
        is_optional = False

    if list_def := is_list_definition(t):
        ret = GqlTypeHinter(
            type=list,
            of_type=(evaluate_field_type(list_def.of_type),),
            scalars=type_info.custom_scalars,
        )
    elif scalar_def := is_scalar_definition(t):
        if builtin_scalar := BuiltinScalars.by_graphql_name(scalar_def.name):
            ret = GqlTypeHinter(type=builtin_scalar, scalars=type_info.custom_scalars)
        else:
            ret = GqlTypeHinter(
                type=type_info.custom_scalars[scalar_def.name],
                scalars=type_info.custom_scalars,
            )
    elif enum_def := is_enum_definition(t):
        ret = GqlTypeHinter(
            type=anti_forward_ref(name=enum_def.name, type_map=type_info.enums),
            scalars=type_info.custom_scalars,
        )
    elif obj_def := is_object_definition(t):
        ret = GqlTypeHinter(
            type=anti_forward_ref(name=obj_def.name, type_map=type_info.object_types),
            scalars=type_info.custom_scalars,
        )
    elif union_def := is_union_definition(t):
        ret = GqlTypeHinter(
            type=Union,
            of_type=tuple(
                GqlTypeHinter(
                    type=anti_forward_ref(
                        name=possible.name,
                        type_map=type_info._object_types,
                    ),
                    scalars=type_info.custom_scalars,
                )
                for possible in type_info.schema_definition.get_possible_types(union_def)
            ),
            scalars=type_info.custom_scalars,
        )
    elif input_def := is_input_definition(t):
        concrete = type_info.schema_definition.get_type(input_def.name)
        assert isinstance(concrete, gql_def.GraphQLInputObjectType)
        ret = GqlTypeHinter(
            type=evaluate_input_type(type_info, input_def),
            scalars=type_info.custom_scalars,
        )

    elif interface_def := is_interface_definition(t):
        ret = GqlTypeHinter(
            type=evaluate_interface_type(interface_def),
            of_type=(),
            scalars=type_info.custom_scalars,
        )
    if not ret:  # pragma: no cover
        raise NotImplementedError(f"type {t} not supported yet")

    if is_optional:
        return GqlTypeHinter(type=Optional, of_type=(ret,), scalars=type_info.custom_scalars)
    return ret


def evaluate_field(
    type_info: SchemaTypeInfo,
    name: str,
    field: gql_def.GraphQLField,
) -> QtGqlFieldDefinition:
    ret = QtGqlFieldDefinition(
        type=evaluate_field_type(type_info, field.type),
        name=name,
        type_info=type_info,
        description=field.description,
    )
    ret.arguments = [
        _evaluate_input_field(type_info, name, arg) for name, arg in field.args.items()
    ]

    return ret


def _evaluate_input_field(
    type_info: SchemaTypeInfo,
    name: str,
    field: gql_def.GraphQLInputField,
) -> QtGqlInputFieldDefinition:
    return QtGqlInputFieldDefinition(
        type=evaluate_field_type(type_info, field.type),
        name=name,
        type_info=type_info,
        description=field.description,
    )


def evaluate_object_type(
    type_info: SchemaTypeInfo,
    type_: gql_def.GraphQLObjectType,
) -> QtGqlObjectTypeDefinition | None:
    t_name: str = type_.name
    if evaluated := type_info.get_object_type(t_name):
        return evaluated
    if type_.name not in type_info.root_types_names:
        # TODO(nir): remove this check.
        # https://github.com/qtgql/qtgql/issues/265
        try:
            id_field = type_.fields["id"]
            if nonull := is_non_null_definition(id_field.type):
                id_scalar = graphql.type.scalars.GraphQLID
                if nonull.of_type is not id_scalar:
                    raise QtGqlException(
                        f"id field type must be of the {id_scalar} scalar!"
                        f"\n Got: {nonull.of_type}",
                    )
            else:
                warnings.warn(
                    stacklevel=2,
                    message="It is best practice to have id field of type ID!"
                    f"\ntype {type_} has: {id_field}",
                )
        except KeyError:
            warnings.warn(
                stacklevel=2,
                message="QtGql enforces types to have ID field"
                f"type {type_} does not not define an id field.\n"
                f"fields: {type_.fields}",
            )
    implements = [evaluate_interface_type(type_info, interface) for interface in type_.interfaces]

    ret = QtGqlObjectTypeDefinition(
        name=t_name,
        interfaces_raw=implements,
        docstring=type_.description,
        fields_dict={
            name: evaluate_field(type_info, name, field) for name, field in type_.fields.items()
        },
    )
    type_info.set_objecttype(ret)
    for interface in type_.interfaces:
        qtgql_interface = evaluate_interface_type(type_info, interface)
        qtgql_interface.implementations[type_.name] = ret
    return ret


def evaluate_interface_type(
    type_info: SchemaTypeInfo,
    interface: gql_def.GraphQLInterfaceType,
) -> QtGqlInterfaceDefinition:
    if ret := type_info.interfaces.get(interface.name, None):
        return ret
    implements = [evaluate_interface_type(type_info, base) for base in interface.interfaces]
    ret = QtGqlInterfaceDefinition(
        name=interface.name,
        interfaces_raw=implements,
        docstring=interface.description,
        fields_dict={
            name: evaluate_field(type_info, name, field) for name, field in interface.fields.items()
        },
    )
    type_info.interfaces[ret.name] = ret
    return ret


def evaluate_enum(
    type_info: SchemaTypeInfo,
    enum: gql_def.GraphQLEnumType,
) -> QtGqlEnumDefinition | None:
    name: str = enum.name

    if definition := type_info.enums.get(name, None):
        return definition

    ret = QtGqlEnumDefinition(
        name=name,
        members=[
            EnumValue(name=enum.value, index=index, description=enum.description or "")
            for index, enum in enumerate(enum.values.values())
        ],
    )

    type_info.enums[name] = ret
    return ret


def evaluate_variable(
    type_info: SchemaTypeInfo,
    var: gql_lang.VariableDefinitionNode,
) -> QtGqlVariableDefinition:
    return QtGqlVariableDefinition(
        name=var.variable.name.value,
        type=type_info.get_type(var.type),
        type_info=type_info,
        default_value=var.default_value,
    )


def evaluate_schema(
    schema: gql_def.GraphQLSchema,
    custom_scalars: CustomScalarMap,
) -> SchemaTypeInfo:
    type_info = SchemaTypeInfo(schema, custom_scalars)
    for name, type_ in type_info.schema_definition.type_map.items():
        if name.startswith("__"):
            continue
        if object_definition := is_object_definition(type_):
            if object_type := evaluate_object_type(type_info, object_definition):
                if object_definition is type_info.schema_definition.query_type:
                    type_info.operation_types[OperationType.QUERY] = object_type
                elif object_definition is type_info.schema_definition.mutation_type:
                    type_info.operation_types[OperationType.MUTATION] = object_type
                elif object_definition is type_info.schema_definition.subscription_type:
                    type_info.operation_types[OperationType.SUBSCRIPTION] = object_type

        elif enum_def := is_enum_definition(type_):
            if enum := evaluate_enum(type_info, enum_def):
                type_info.enums[enum.name] = enum

    return type_info
