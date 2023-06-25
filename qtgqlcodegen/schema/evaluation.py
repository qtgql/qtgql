from __future__ import annotations

from typing import NamedTuple

from graphql import OperationType
from graphql.type import definition as gql_def

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
from qtgqlcodegen.schema.definitions import (
    CustomScalarMap,
    QtGqlArgumentDefinition,
    QtGqlFieldDefinition,
    SchemaTypeInfo,
)
from qtgqlcodegen.types import (
    BuiltinScalars,
    EnumValue,
    QtGqlDeferredType,
    QtGqlEnumDefinition,
    QtGqlInputObjectTypeDefinition,
    QtGqlInterface,
    QtGqlList,
    QtGqlObjectType,
    QtGqlOptional,
    QtGqlTypeABC,
    QtGqlUnion,
)


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
                name: _evaluate_argument_field(type_info, name, field)
                for name, field in type_.fields.items()
            },
        )
        type_info.input_objects[ret.name] = ret
    return ret


def evaluate_graphql_type(
    type_info: SchemaTypeInfo,
    t: gql_def.GraphQLType,
) -> QtGqlTypeABC:
    # even though every type in qtgql has a default constructor,
    # hence there is no "real" non-null values
    # we store it as optional for generating nullable checks only for what's required.
    ret: QtGqlTypeABC | None = None
    is_optional = True
    if non_null := is_non_null_definition(t):
        t = non_null.of_type
        is_optional = False

    if list_def := is_list_definition(t):
        ret = QtGqlList(
            of_type=evaluate_graphql_type(type_info, list_def.of_type),
        )
    elif scalar_def := is_scalar_definition(t):
        if builtin_scalar := BuiltinScalars.by_graphql_name(scalar_def.name):
            ret = builtin_scalar
        else:
            ret = type_info.custom_scalars[scalar_def.name]

    elif enum_def := is_enum_definition(t):
        ret = _evaluate_enum(type_info, enum_def)

    elif obj_def := is_object_definition(t):
        ret = QtGqlDeferredType(
            object_map__=type_info.object_types,
            name=obj_def.name,
        )
    elif union_def := is_union_definition(t):
        ret = QtGqlUnion(
            types=tuple(
                QtGqlDeferredType(
                    name=possible.name,
                    object_map__=type_info.object_types,
                )
                for possible in type_info.schema_definition.get_possible_types(union_def)
            ),
        )
    elif input_def := is_input_definition(t):
        concrete = type_info.schema_definition.get_type(input_def.name)
        assert isinstance(concrete, gql_def.GraphQLInputObjectType)
        ret = evaluate_input_type(type_info, input_def)

    elif interface_def := is_interface_definition(t):
        ret = _evaluate_interface_type(type_info, interface_def)
    if not ret:  # pragma: no cover
        raise NotImplementedError(f"type {t} not supported yet")

    if is_optional:
        return QtGqlOptional(of_type=ret)
    return ret


def evaluate_field(
    type_info: SchemaTypeInfo,
    name: str,
    field: gql_def.GraphQLField,
) -> QtGqlFieldDefinition:
    return QtGqlFieldDefinition(
        type=evaluate_graphql_type(type_info, field.type),
        name=name,
        description=field.description,
        arguments_dict={
            name: _evaluate_argument_field(type_info, name, arg) for name, arg in field.args.items()
        },
    )


def _evaluate_argument_field(
    type_info: SchemaTypeInfo,
    name: str,
    field: gql_def.GraphQLInputField | gql_def.GraphQLArgument,
) -> QtGqlArgumentDefinition:
    return QtGqlArgumentDefinition(
        type=evaluate_graphql_type(type_info, field.type),
        name=name,
        description=field.description,
    )


class InterfaceOrObjectOptions(NamedTuple):
    implements: tuple[QtGqlInterface, ...]
    all_fields: dict[str, QtGqlFieldDefinition]
    unique_fields: tuple[QtGqlFieldDefinition, ...]


def _evaluate_object_fields(
    type_info: SchemaTypeInfo,
    obj: gql_def.GraphQLObjectType | gql_def.GraphQLInterfaceType,
) -> InterfaceOrObjectOptions:
    implements = tuple(
        _evaluate_interface_type(type_info, interface) for interface in obj.interfaces
    )
    inherited_fields = {}
    for i in implements:
        inherited_fields.update(i.fields_dict)

    self_fields: dict[str, QtGqlFieldDefinition] = {
        name: evaluate_field(type_info, name, field)
        for name, field in obj.fields.items()
        if name not in inherited_fields.keys()
    }

    inherited_fields.update(self_fields)
    return InterfaceOrObjectOptions(
        implements=implements,
        all_fields=inherited_fields,
        unique_fields=tuple(self_fields.values()),
    )


def _evaluate_object_type(
    type_info: SchemaTypeInfo,
    type_: gql_def.GraphQLObjectType,
) -> QtGqlObjectType | None:
    t_name: str = type_.name
    if evaluated := type_info.get_object_type(t_name):
        return evaluated

    options = _evaluate_object_fields(type_info, type_)

    ret = QtGqlObjectType(
        name=t_name,
        interfaces_raw=options.implements,
        docstring=type_.description,
        fields_dict=options.all_fields,
        unique_fields=options.unique_fields,
        is_root=t_name in type_info.root_types_names,
    )
    type_info.add_objecttype(ret)
    for interface in type_.interfaces:
        qtgql_interface = _evaluate_interface_type(type_info, interface)
        qtgql_interface.implementations[type_.name] = ret
    return ret


def _evaluate_interface_type(
    type_info: SchemaTypeInfo,
    interface: gql_def.GraphQLInterfaceType,
) -> QtGqlInterface:
    if ret := type_info.interfaces.get(interface.name, None):
        return ret
    options = _evaluate_object_fields(type_info, interface)
    ret = QtGqlInterface(
        name=interface.name,
        interfaces_raw=options.implements,
        docstring=interface.description,
        fields_dict=options.all_fields,
        unique_fields=options.unique_fields,
    )
    if ret.name == "Node":
        id_field = ret.fields[0]
        if id_field.type != BuiltinScalars.ID or id_field.type.is_optional:
            raise QtGqlException(
                f"Node is a reserved type, id field on `Node` interface must be of type `ID!`"
                f"\n Got: {interface.fields['id']}",
            )
    type_info.interfaces[ret.name] = ret
    return ret


def _evaluate_enum(
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


def evaluate_schema(
    schema: gql_def.GraphQLSchema,
    custom_scalars: CustomScalarMap,
) -> SchemaTypeInfo:
    type_info = SchemaTypeInfo(schema, custom_scalars)
    for name, type_ in type_info.schema_definition.type_map.items():
        if name.startswith("__"):
            continue
        if object_definition := is_object_definition(type_):
            if object_type := _evaluate_object_type(type_info, object_definition):
                if object_definition is type_info.schema_definition.query_type:
                    type_info.operation_types[OperationType.QUERY.value] = object_type
                elif object_definition is type_info.schema_definition.mutation_type:
                    type_info.operation_types[OperationType.MUTATION.value] = object_type
                elif object_definition is type_info.schema_definition.subscription_type:
                    type_info.operation_types[OperationType.SUBSCRIPTION.value] = object_type

        elif enum_def := is_enum_definition(type_):
            if enum := _evaluate_enum(type_info, enum_def):
                type_info.enums[enum.name] = enum

    return type_info
