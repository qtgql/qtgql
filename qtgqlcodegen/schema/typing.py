from __future__ import annotations

import contextlib
from functools import cached_property
from typing import TYPE_CHECKING, Any

from attr import Factory, define
from graphql import OperationType
from typingref import TypeHinter

from qtgqlcodegen.builtin_scalars import BuiltinScalar, BuiltinScalars
from qtgqlcodegen.operation.definitions import QtGqlQueriedObjectType
from qtgqlcodegen.schema.definitions import (
    QtGqlEnumDefinition,
    QtGqlInputObjectTypeDefinition,
    QtGqlInterfaceDefinition,
    QtGqlObjectTypeDefinition,
)
from qtgqlcodegen.utils import AntiForwardRef, freeze

if TYPE_CHECKING:
    from graphql.type import definition as gql_def
    from typing_extensions import TypeAlias

    from qtgqlcodegen.custom_scalars import CustomScalarDefinition

EnumMap: TypeAlias = "dict[str, QtGqlEnumDefinition]"
ObjectTypeMap: TypeAlias = "dict[str, QtGqlObjectTypeDefinition]"
InputObjectMap: TypeAlias = "dict[str, QtGqlInputObjectTypeDefinition]"
InterfacesMap: TypeAlias = "dict[str, QtGqlInterfaceDefinition]"
CustomScalarMap: TypeAlias = "dict[str, CustomScalarDefinition]"


@define(slots=False)
class SchemaTypeInfo:
    schema_definition: gql_def.GraphQLSchema
    custom_scalars: CustomScalarMap
    operation_types: dict[OperationType:QtGqlObjectTypeDefinition] = Factory(dict)
    object_types: ObjectTypeMap = Factory(dict)
    enums: EnumMap = Factory(dict)
    input_objects: InputObjectMap = Factory(dict)
    interfaces: InterfacesMap = Factory(dict)

    def get_interface_by_name(self, name: str) -> QtGqlInterfaceDefinition | None:
        return self.interfaces.get(name, None)

    def get_objecttype_by_name(self, name: str) -> QtGqlObjectTypeDefinition | None:
        return self.object_types.get(name, None)

    @cached_property
    def root_types(self) -> list[gql_def.GraphQLObjectType | None]:
        return [
            self.schema_definition.get_root_type(OperationType.QUERY),
            self.schema_definition.get_root_type(OperationType.MUTATION),
            self.schema_definition.get_root_type(OperationType.SUBSCRIPTION),
        ]

    @cached_property
    def root_types_names(self) -> str:
        return " ".join([tp.name for tp in self.root_types if tp])


class GqlTypeHinter(TypeHinter):
    def __init__(
        self,
        type: Any,
        scalars: CustomScalarMap,
        of_type: tuple[GqlTypeHinter, ...] = (),
    ):
        self.type = type
        self.of_type: tuple[GqlTypeHinter, ...] = of_type
        self.scalars = scalars
        self.__setattr__ = freeze

    @cached_property
    def optional_maybe(self) -> GqlTypeHinter:
        return self if not super().is_optional() else self.of_type[0]

    @cached_property
    def is_union(self) -> bool:
        return super().is_union()

    @cached_property
    def is_object_type(self) -> QtGqlObjectTypeDefinition | None:
        t_self = self.optional_maybe.type
        if self.is_interface:
            return None
        with contextlib.suppress(TypeError):
            if issubclass(t_self, AntiForwardRef):
                ret = t_self.resolve()
                if isinstance(ret, QtGqlObjectTypeDefinition):
                    return ret

    @cached_property
    def is_queried_object_type(self) -> QtGqlQueriedObjectType | None:
        t_self = self.optional_maybe.type
        if isinstance(t_self, QtGqlQueriedObjectType):
            return t_self

    @cached_property
    def is_input_object_type(self) -> QtGqlInputObjectTypeDefinition | None:
        t_self = self.optional_maybe.type
        if isinstance(t_self, QtGqlInputObjectTypeDefinition):
            return t_self

    @cached_property
    def is_model(self) -> GqlTypeHinter | None:
        t_self = self.optional_maybe
        if t_self.is_list():
            # scalars or unions are not supported in lists yet (valid graphql spec though)
            return t_self.of_type[0]

    @cached_property
    def is_interface(self) -> QtGqlInterfaceDefinition | None:
        t_self = self.optional_maybe.type
        if isinstance(t_self, QtGqlInterfaceDefinition):
            return t_self

    @cached_property
    def is_enum(self) -> QtGqlEnumDefinition | None:
        t_self = self.optional_maybe.type
        with contextlib.suppress(TypeError):
            if issubclass(t_self, AntiForwardRef):
                if isinstance(t_self.resolve(), QtGqlEnumDefinition):
                    return t_self.resolve()

    @cached_property
    def is_builtin_scalar(self) -> BuiltinScalar | None:
        t_self = self.optional_maybe.type
        if isinstance(t_self, BuiltinScalar):
            return t_self

    @property
    def is_void(self) -> bool:
        if sc := self.is_builtin_scalar:
            return sc is BuiltinScalars.VOID
        return False

    @cached_property
    def is_custom_scalar(self) -> CustomScalarDefinition | None:
        t_self = self.optional_maybe.type
        if t_self in self.scalars.values():
            return t_self

    @cached_property
    def type_name(self) -> str:
        t_self = self.optional_maybe
        if builtin_scalar := t_self.is_builtin_scalar:
            return builtin_scalar.attr.name

        if scalar := t_self.is_custom_scalar:
            return scalar.type_name

        if enum_def := t_self.is_enum:
            return enum_def.namespaced_name

        if t_self.is_model:
            # map of instances based on operation hash.
            raise NotImplementedError(
                "models have no valid type for schema concretes, call member_type()",
            )

        if object_def := t_self.is_object_type or t_self.is_interface:
            return object_def.name
        if q_object_def := t_self.is_queried_object_type:
            return q_object_def.name
        if t_self.is_union:
            raise NotImplementedError
        if input_obj := t_self.is_input_object_type:
            return input_obj.name
        raise NotImplementedError  # pragma no cover

    @cached_property
    def member_type(self) -> str:
        """
        :returns: Annotation of the field at the concrete type (for the type of the proxy use property type)
        """
        t_self = self.optional_maybe

        if model_of := t_self.is_model:
            # map of instances based on operation id.
            return f"QMap<QUuid, QList<{model_of.member_type}>>"
        if t_self.is_object_type or t_self.is_interface:
            return f"std::shared_ptr<{self.type_name}>"
        if q_object_def := t_self.is_queried_object_type:
            return f"{q_object_def.name}"
        return self.type_name

    def as_annotation(self, object_map=None):  # pragma: no cover
        raise NotImplementedError("not safe to call on this type")
