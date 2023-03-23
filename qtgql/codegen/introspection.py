from __future__ import annotations

import warnings
from functools import cached_property
from typing import (
    TYPE_CHECKING,
    List,
    Optional,
    TypedDict,
    Union,
)

import graphql
from graphql import OperationType
from graphql import language as gql_lang
from graphql.language import visitor
from graphql.type import definition as gql_def

from qtgql.codegen.graphql_ref import (
    is_enum_definition,
    is_input_definition,
    is_list_definition,
    is_named_type_node,
    is_non_null_definition,
    is_nonnull_node,
    is_object_definition,
    is_operation_def_node,
    is_scalar_definition,
    is_union_definition,
)
from qtgql.codegen.py.compiler.builtin_scalars import BuiltinScalars
from qtgql.codegen.py.compiler.query import QtGqlOperationDefinition, QtGqlQueriedField
from qtgql.codegen.py.compiler.template import (
    TemplateContext,
    handlers_template,
    schema_types_template,
)
from qtgql.codegen.py.objecttype import (
    EnumMap,
    EnumValue,
    GqlTypeHinter,
    QtGqlEnumDefinition,
    QtGqlFieldDefinition,
    QtGqlInputFieldDefinition,
    QtGqlInputObjectTypeDefinition,
    QtGqlObjectTypeDefinition,
    QtGqlVariableDefinition,
)
from qtgql.codegen.utils import anti_forward_ref
from qtgql.exceptions import QtGqlException

if TYPE_CHECKING:  # pragma: no cover
    from qtgql.codegen.py.compiler.config import QtGqlConfig

introspection_query = graphql.get_introspection_query(descriptions=True)


class GeneratedNamespace(TypedDict):
    handlers: str
    objecttypes: str


class QtGqlVisitor(visitor.Visitor):
    """Creates handlers for root operations.

    Also injects id field to types that have id field but not explicitly
    queried it.
    """

    def __init__(self, evaluator: SchemaEvaluator):
        super().__init__()
        self.query_handlers: dict[str, QtGqlOperationDefinition] = {}
        self.mutation_handlers: dict[str, QtGqlOperationDefinition] = {}
        self.evaluator = evaluator

    def _get_root_type_field(
        self,
        root_type: QtGqlObjectTypeDefinition,
        gql_field: gql_lang.FieldNode,
    ) -> QtGqlQueriedField:
        return QtGqlQueriedField.from_field(
            root_type.fields_dict[gql_field.name.value],
            gql_field.selection_set,
        )

    def _parse_variable_definition(
        self,
        var: gql_lang.VariableDefinitionNode,
    ) -> QtGqlVariableDefinition:
        return QtGqlVariableDefinition(
            name=var.variable.name.value,
            type=self.evaluator.get_type(var.type),
            type_map=self.evaluator._objecttypes_def_map,
            scalars=self.evaluator.config.custom_scalars,
            enums=self.evaluator._enums_def_map,
            default_value=var.default_value,
        )

    def enter_operation_definition(self, node, key, parent, path, ancestors) -> None:
        if operation := is_operation_def_node(node):
            if operation.operation in (OperationType.QUERY, OperationType.MUTATION):
                root_field: gql_lang.FieldNode = operation.selection_set.selections[0]  # type: ignore
                assert operation.name, "QtGql enforces operations to have names."
                op_name = operation.name.value
                operation_vars: list[QtGqlVariableDefinition] = []
                if variables_def := operation.variable_definitions:
                    for var in variables_def:
                        operation_vars.append(self._parse_variable_definition(var))
                if operation.operation is OperationType.QUERY:
                    assert self.evaluator._query_type
                    root_qtgql_field = self._get_root_type_field(
                        self.evaluator._query_type,
                        root_field,
                    )
                    operation_definition = QtGqlOperationDefinition(
                        query=graphql.print_ast(node),
                        name=op_name,
                        field=root_qtgql_field,
                        directives=node.directives,
                        variables=operation_vars,
                    )
                    self.query_handlers[op_name] = operation_definition
                elif operation.operation is OperationType.MUTATION:
                    assert (
                        self.evaluator._mutation_type
                    ), "You don't have any mutations on your schema"
                    root_qtgql_field = self._get_root_type_field(
                        self.evaluator._mutation_type,
                        root_field,
                    )
                    operation_definition = QtGqlOperationDefinition(
                        query=graphql.print_ast(node),
                        name=op_name,
                        field=root_qtgql_field,
                        directives=node.directives,
                        variables=operation_vars,
                    )
                    self.mutation_handlers[op_name] = operation_definition


class SchemaEvaluator:
    def __init__(self, config: QtGqlConfig):
        self.config = config
        self._objecttypes_def_map: dict[str, QtGqlObjectTypeDefinition] = {}
        self._enums_def_map: EnumMap = {}
        self._input_objects_def_map: dict[str, QtGqlInputObjectTypeDefinition] = {}
        self._query_handlers: dict[str, QtGqlOperationDefinition] = {}
        self._mutation_handlers: dict[str, QtGqlOperationDefinition] = {}
        self._query_type: Optional[QtGqlObjectTypeDefinition] = None
        self._mutation_type: Optional[QtGqlObjectTypeDefinition] = None

    def get_type(self, node: gql_lang.TypeNode) -> GqlTypeHinter:
        if nonnull := is_nonnull_node(node):
            return self._evaluate_field_type(
                graphql.type.GraphQLNonNull(
                    self.schema_definition.get_type(nonnull.type.name.value),  # type: ignore
                ),
            )

        if named_type := is_named_type_node(node):
            gql_concrete = self.schema_definition.get_type(named_type.name.value)
            assert gql_concrete
            return self._evaluate_field_type(gql_concrete)
        raise NotImplementedError(node, "Type is not supported as a variable ATM")

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
        # even though every type in qtgql has a default constructor,
        # hence there is no "real" non-null values
        # we store it as optional for generating nullable checks only for what's required.
        ret = None
        is_optional = True
        if non_null := is_non_null_definition(t):
            t = non_null.of_type
            is_optional = False

        if list_def := is_list_definition(t):
            ret = GqlTypeHinter(type=list, of_type=(self._evaluate_field_type(list_def.of_type),))
        elif scalar_def := is_scalar_definition(t):
            if builtin_scalar := BuiltinScalars.by_graphql_name(scalar_def.name):
                ret = GqlTypeHinter(type=builtin_scalar)
            else:
                ret = GqlTypeHinter(type=self.config.custom_scalars[scalar_def.name])
        elif enum_def := is_enum_definition(t):
            ret = GqlTypeHinter(
                type=anti_forward_ref(name=enum_def.name, type_map=self._enums_def_map),
            )
        elif obj_def := is_object_definition(t):
            ret = GqlTypeHinter(
                type=anti_forward_ref(name=obj_def.name, type_map=self._objecttypes_def_map),
            )
        elif union_def := is_union_definition(t):
            ret = GqlTypeHinter(
                type=Union,
                of_type=tuple(
                    GqlTypeHinter(
                        type=anti_forward_ref(
                            name=possible.name,
                            type_map=self._objecttypes_def_map,
                        ),
                    )
                    for possible in self.schema_definition.get_possible_types(union_def)
                ),
            )
        elif input_def := is_input_definition(t):
            concrete = self.schema_definition.get_type(input_def.name)
            assert isinstance(concrete, gql_def.GraphQLInputObjectType)
            ret = GqlTypeHinter(type=self._evaluate_input_type(input_def))

        if not ret:  # pragma: no cover
            raise NotImplementedError(f"type {t} not supported yet")

        if is_optional:
            return GqlTypeHinter(type=Optional, of_type=(ret,))
        return ret

    def _evaluate_field(self, name: str, field: gql_def.GraphQLField) -> QtGqlFieldDefinition:
        return QtGqlFieldDefinition(
            type=self._evaluate_field_type(field.type),
            name=name,
            type_map=self._objecttypes_def_map,
            scalars=self.config.custom_scalars,
            enums=self._enums_def_map,
            description=field.description,
        )

    def _evaluate_input_field(
        self,
        name: str,
        field: gql_def.GraphQLInputField,
    ) -> QtGqlInputFieldDefinition:
        return QtGqlInputFieldDefinition(
            type=self._evaluate_field_type(field.type),
            name=name,
            type_map=self._objecttypes_def_map,
            scalars=self.config.custom_scalars,
            enums=self._enums_def_map,
            description=field.description,
        )

    def _evaluate_object_type(
        self,
        type_: gql_def.GraphQLObjectType,
    ) -> Optional[QtGqlObjectTypeDefinition]:
        t_name: str = type_.name
        if evaluated := self._objecttypes_def_map.get(t_name, None):
            return evaluated
        if type_ not in self.root_types:
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
        ret = QtGqlObjectTypeDefinition(
            name=t_name,
            docstring=type_.description,
            fields_dict={
                name: self._evaluate_field(name, field) for name, field in type_.fields.items()
            },
        )
        assert ret not in self.root_types
        self._objecttypes_def_map[ret.name] = ret
        return ret

    def _evaluate_input_type(self, type_: gql_def.GraphQLInputObjectType):
        ret = self._input_objects_def_map.get(type_.name, None)
        if not ret:
            ret = QtGqlInputObjectTypeDefinition(
                name=type_.name,
                docstring=type_.description,
                fields_dict={
                    name: self._evaluate_input_field(name, field)
                    for name, field in type_.fields.items()
                },
            )
            self._input_objects_def_map[ret.name] = ret
        return ret

    def _evaluate_enum(self, enum: gql_def.GraphQLEnumType) -> Optional[QtGqlEnumDefinition]:
        name: str = enum.name

        if self._enums_def_map.get(name, None):
            return None

        return QtGqlEnumDefinition(
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
                    elif object_definition is self.schema_definition.mutation_type:
                        self._mutation_type = object_type

            elif enum_def := is_enum_definition(type_):
                if enum := self._evaluate_enum(enum_def):
                    self._enums_def_map[enum.name] = enum

    def parse_operations(self) -> None:
        with (self.config.graphql_dir / "operations.graphql").open() as f:
            operations = graphql.parse(f.read())

        # validate the operation against the static schema
        if errors := graphql.validate(self.schema_definition, operations):
            raise QtGqlException([error.formatted for error in errors])

        # get QtGql fields from the query AST and inject ID field.
        operation_miner = QtGqlVisitor(self)
        visitor.visit(operations, operation_miner)
        self._query_handlers.update(operation_miner.query_handlers)
        self._mutation_handlers.update(operation_miner.mutation_handlers)

    def dumps(self) -> GeneratedNamespace:
        """:return: The generated modules as a string."""
        self.parse_schema_concretes()
        self.parse_operations()
        context = TemplateContext(
            enums=list(self._enums_def_map.values()),
            types=[
                t
                for name, t in self._objecttypes_def_map.items()
                if name not in BuiltinScalars.keys()
            ],
            queries=list(self._query_handlers.values()),
            mutations=list(self._mutation_handlers.values()),
            input_objects=list(self._input_objects_def_map.values()),
            config=self.config,
        )
        return GeneratedNamespace(
            handlers=handlers_template(context),
            objecttypes=schema_types_template(context),
        )

    def dump(self):
        """:param file: Path to the directory the codegen would dump to."""
        for fname, content in self.dumps().items():
            with (self.config.graphql_dir / (fname + ".py")).open("w") as fh:
                fh.write(content)
