from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Callable, NewType, Optional, Type, TypedDict, TypeVar, Union

import graphql
from graphql import OperationType
from graphql.type import definition as gql_def

from qtgql.codegen.py.compiler.builtin_scalars import BuiltinScalars
from qtgql.codegen.py.compiler.query import QueryHandlerDefinition
from qtgql.codegen.py.compiler.template import (
    TemplateContext,
    handlers_template,
    schema_types_template,
)
from qtgql.codegen.py.objecttype import (
    EnumMap,
    EnumValue,
    GqlEnumDefinition,
    GqlFieldDefinition,
    GqlTypeDefinition,
    GqlTypeHinter,
)
from qtgql.codegen.utils import anti_forward_ref
from qtgql.exceptions import QtGqlException

if TYPE_CHECKING:  # pragma: no cover
    from qtgql.codegen.py.compiler.config import QtGqlConfig

introspection_query = graphql.get_introspection_query(descriptions=True)


OperationName = NewType("OperationName", str)


class GeneratedNamespace(TypedDict):
    handlers: str
    objecttypes: str


class SchemaEvaluator:
    def __init__(self, config: QtGqlConfig):
        self.config = config
        self._generated_types: dict[str, GqlTypeDefinition] = {}
        self._generated_enums: EnumMap = {}
        self._fragments_store: dict[int, str] = {}
        self._query_handlers: dict[OperationName, QueryHandlerDefinition] = {}

    @cached_property
    def schema_definition(self) -> graphql.GraphQLSchema:
        with open(self.config.graphql_dir / "schema.graphql", "r") as f:
            return graphql.build_schema(f.read())

    @property
    def query_type(self) -> GqlTypeDefinition:
        query_type = self.schema_definition.query_type
        assert query_type
        return self._generated_types[query_type.name]

    def _evaluate_field_type(self, t: gql_def.GraphQLType) -> GqlTypeHinter:
        if non_null := is_non_null_definition(t):
            # There are no optionals in qtgql, we use default values.
            # By default, everything in graphql is optional,
            # so NON_NULL doesn't really make a difference,
            return self._evaluate_field_type(non_null.of_type)

        if list_def := is_list_definition(t):
            return GqlTypeHinter(type=list, of_type=(self._evaluate_field_type(list_def.of_type),))
        elif scalar_def := is_scalar_definition(t):
            if builtin_scalar := BuiltinScalars.by_graphql_name(scalar_def.name):
                return GqlTypeHinter(type=builtin_scalar)
            else:
                return GqlTypeHinter(type=self.config.custom_scalars[scalar_def.name])
        elif enum_def := is_enum_definition(t):
            return GqlTypeHinter(
                type=anti_forward_ref(name=enum_def.name, type_map=self._generated_enums)
            )
        elif obj_def := is_object_definition(t):
            return GqlTypeHinter(
                type=anti_forward_ref(name=obj_def.name, type_map=self._generated_types)
            )
        elif union_def := is_union_definition(t):
            return GqlTypeHinter(
                type=Union,
                of_type=tuple(
                    GqlTypeHinter(
                        type=anti_forward_ref(name=possible.name, type_map=self._generated_types)
                    )
                    for possible in self.schema_definition.get_possible_types(union_def)
                ),
            )

        raise NotImplementedError(f"type {t} not supported yet")  # pragma: no cover

    def _evaluate_field(self, name: str, field: gql_def.GraphQLField) -> GqlFieldDefinition:
        """we don't really know what is the field type just it's name."""
        return GqlFieldDefinition(
            type=self._evaluate_field_type(field.type),
            name=name,
            type_map=self._generated_types,
            scalars=self.config.custom_scalars,
            description=field.description,
            enums=self._generated_enums,
        )

    def _evaluate_object_type(
        self, type_: gql_def.GraphQLObjectType
    ) -> Optional[GqlTypeDefinition]:
        t_name: str = type_.name
        if t_name.startswith("__"):
            return None
        if evaluated := self._generated_types.get(t_name, None):
            return evaluated

        concrete = GqlTypeDefinition(
            name=t_name,
            docstring=type_.description,
            fields=[self._evaluate_field(name, field) for name, field in type_.fields.items()],
        )
        return concrete

    def _evaluate_enum(self, enum: gql_def.GraphQLEnumType) -> Optional[GqlEnumDefinition]:
        name: str = enum.name

        if self._generated_enums.get(name, None):
            return None

        return GqlEnumDefinition(
            name=name,
            members=[
                EnumValue(name=name, description=val.description or "")
                for name, val in enum.values.items()
            ],
        )

    def parse_schema_concretes(self) -> None:
        for name, type_ in self.schema_definition.type_map.items():
            if name.startswith("__"):
                continue

            if object_definition := is_object_definition(type_):
                if object_type := self._evaluate_object_type(object_definition):
                    self._generated_types[object_type.name] = object_type
            elif enum_def := is_enum_definition(type_):
                if enum := self._evaluate_enum(enum_def):
                    self._generated_enums[enum.name] = enum

    def parse_queries(self) -> None:
        with open(self.config.graphql_dir / "operations.graphql", "r") as f:
            queries = graphql.parse(f.read())

        if errors := graphql.validate(self.schema_definition, queries):
            raise QtGqlException([error.formatted for error in errors])

        for definition in queries.definitions:
            field_name = definition.selection_set.selections[0].name.value  # type: ignore
            field = None
            if definition.operation is OperationType.QUERY:  # type: ignore
                for field_impl in self.query_type.fields:
                    if field_impl.name == field_name:
                        field = field_impl
                assert field
                op_name = OperationName(definition.name.value)  # type: ignore
                self._query_handlers[op_name] = QueryHandlerDefinition(
                    query=graphql.print_ast(definition),
                    name=op_name,
                    field=field,
                    directives=definition.directives,  # type: ignore
                )

    def dumps(self) -> GeneratedNamespace:
        """:return: The generated schema module as a string."""
        self.parse_schema_concretes()
        self.parse_queries()
        context = TemplateContext(
            enums=list(self._generated_enums.values()),
            types=[
                t for name, t in self._generated_types.items() if name not in BuiltinScalars.keys()
            ],
            queries=list(self._query_handlers.values()),
            config=self.config,
        )
        return GeneratedNamespace(
            handlers=handlers_template(context), objecttypes=schema_types_template(context)
        )

    def dump(self):
        """:param file: Path to the directory the codegen would dump to."""
        for fname, content in self.dumps().items():
            with open(self.config.graphql_dir / (fname + ".py"), "w") as fh:
                fh.write(content)


T_Definition = TypeVar("T_Definition", bound=gql_def.GraphQLType)


def definition_identifier_factory(
    expected: Type[T_Definition],
) -> Callable[[gql_def.GraphQLType], Optional[T_Definition]]:
    def type_guarder(definition: gql_def.GraphQLType) -> Optional[T_Definition]:
        if isinstance(definition, expected):
            return definition

    return type_guarder


is_object_definition = definition_identifier_factory(gql_def.GraphQLObjectType)
is_enum_definition = definition_identifier_factory(gql_def.GraphQLEnumType)
is_list_definition = definition_identifier_factory(gql_def.GraphQLList)
is_scalar_definition = definition_identifier_factory(gql_def.GraphQLScalarType)
is_union_definition = definition_identifier_factory(gql_def.GraphQLUnionType)

is_non_null_definition = definition_identifier_factory(gql_def.GraphQLNonNull)
