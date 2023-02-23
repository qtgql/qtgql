from __future__ import annotations

from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Callable,
    List,
    Optional,
    Type,
    TypedDict,
    TypeVar,
    Union,
)

import graphql
from graphql import OperationType
from graphql import language as gql_lang
from graphql.language import visitor
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


class GeneratedNamespace(TypedDict):
    handlers: str
    objecttypes: str


def has_id_field(selection_set: gql_lang.SelectionSetNode) -> bool:
    if hasattr(selection_set, "__has_id__"):
        return True
    for field in selection_set.selections:
        assert isinstance(field, gql_lang.FieldNode)
        if field.name.value == "id":
            return True
    return False


class IDInjectionVisitor(visitor.Visitor):
    ID_SELECTION_NODE = gql_lang.FieldNode(
        name=gql_lang.NameNode(value="id"), arguments=(), directives=()
    )

    def __init__(self) -> None:
        super().__init__()
        self.modified_source: str = ""

    def enter_field(self, node: gql_def.FieldNode, key, parent, path, ancestors):
        # root field grand parent is an operation.
        if is_operation_def_node(ancestors[-2]):
            return
        selection_set: gql_lang.SelectionSetNode = ancestors[-1]
        assert is_selection_set(selection_set)
        if not has_id_field(selection_set):
            selection_set.selections = (self.ID_SELECTION_NODE, *selection_set.selections)
            selection_set.__has_id__ = True


class OperationMinerVisitor(visitor.Visitor):
    """Creates handlers for root operations."""

    def __init__(self, evaluator: SchemaEvaluator):
        super().__init__()
        self.query_handlers: dict[str, QueryHandlerDefinition] = {}
        self.evaluator = evaluator

    def enter_operation_definition(self, node, key, parent, path, ancestors):
        if operation := is_operation_def_node(node):
            if operation.operation is OperationType.QUERY:  # type: ignore
                fname = operation.selection_set.selections[0].name.value
                assert self.evaluator._query_type
                for field_impl in self.evaluator._query_type.fields:
                    if field_impl.name == fname:
                        field = field_impl
                assert field
                op_name = operation.name.value
                self.query_handlers[op_name] = QueryHandlerDefinition(
                    query=graphql.print_ast(node),
                    name=op_name,
                    field=field,
                    directives=node.directives,
                )


class SchemaEvaluator:
    def __init__(self, config: QtGqlConfig):
        self.config = config
        self._generated_types: dict[str, GqlTypeDefinition] = {}
        self._generated_enums: EnumMap = {}
        self._fragments_store: dict[int, str] = {}
        self._query_handlers: dict[str, QueryHandlerDefinition] = {}
        self._query_type: Optional[GqlTypeDefinition] = None

    @cached_property
    def schema_definition(self) -> graphql.GraphQLSchema:
        with (self.config.graphql_dir / "schema.graphql").open() as f:
            return graphql.build_schema(f.read())

    @cached_property
    def root_types(self) -> List[Optional[gql_def.GraphQLObjectType]]:
        return [
            self.schema_definition.get_root_type(OperationType.QUERY),
            self.schema_definition.get_root_type(OperationType.MUTATION),
            self.schema_definition.get_root_type(OperationType.SUBSCRIPTION),
        ]

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
        if type_ not in self.root_types:
            try:
                id_field = type_.fields["id"]
                if nonull := is_non_null_definition(id_field.type):
                    id_scalar = graphql.type.scalars.GraphQLID
                    if nonull.of_type is not id_scalar:
                        raise QtGqlException(
                            f"id field type must be of the {id_scalar} scalar!"
                            f"\n Got: {nonull.of_type}"
                        )
                else:
                    raise QtGqlException("id field should not be nullable!" f"\n Got: {id_field}")
            except KeyError:
                raise QtGqlException(
                    "QtGql enforces types to have ID field"
                    f"type {type_} does not not define an id field.\n"
                    f"fields: {type_.fields}"
                )
        return GqlTypeDefinition(
            name=t_name,
            docstring=type_.description,
            fields=[self._evaluate_field(name, field) for name, field in type_.fields.items()],
        )

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
                    if object_definition is self.schema_definition.query_type:
                        self._query_type = object_type
                    assert object_type not in self.root_types

                    self._generated_types[object_type.name] = object_type
            elif enum_def := is_enum_definition(type_):
                if enum := self._evaluate_enum(enum_def):
                    self._generated_enums[enum.name] = enum

    def parse_operations(self) -> None:
        with (self.config.graphql_dir / "operations.graphql").open() as f:
            operations = graphql.parse(f.read())

        operations = visitor.visit(operations, IDInjectionVisitor())
        # validate the operation against the static schema
        if errors := graphql.validate(self.schema_definition, operations):
            raise QtGqlException([error.formatted for error in errors])

        # get QtGql fields from the query AST.
        operation_miner = OperationMinerVisitor(self)
        visitor.visit(operations, operation_miner)
        self._query_handlers.update(operation_miner.query_handlers)

    def dumps(self) -> GeneratedNamespace:
        """:return: The generated schema module as a string."""
        self.parse_schema_concretes()
        self.parse_operations()
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
            with (self.config.graphql_dir / (fname + ".py")).open("w") as fh:
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

# Node checks
T_AST_Node = TypeVar("T_AST_Node", bound=gql_lang.Node)


def ast_identifier_factory(
    expected: Type[T_AST_Node],
) -> Callable[[gql_lang.Node], Optional[T_AST_Node]]:
    def type_guarder(node: gql_lang.ast.Node) -> Optional[T_AST_Node]:
        if isinstance(node, expected):
            return node

    return type_guarder


is_selection_set = ast_identifier_factory(gql_lang.ast.SelectionSetNode)
is_operation_def_node = ast_identifier_factory(gql_def.OperationDefinitionNode)
