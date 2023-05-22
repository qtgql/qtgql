from __future__ import annotations

import subprocess
import warnings
from functools import cached_property
from typing import List
from typing import Optional
from typing import TYPE_CHECKING
from typing import TypedDict
from typing import Union

import graphql
from graphql import language as gql_lang
from graphql import OperationType
from graphql.language import visitor
from graphql.type import definition as gql_def

from qtgqlcodegen.compiler.builtin_scalars import BuiltinScalars
from qtgqlcodegen.compiler.operation import QtGqlOperationDefinition
from qtgqlcodegen.compiler.template import cmake_template
from qtgqlcodegen.compiler.template import CmakeTemplateContext
from qtgqlcodegen.compiler.template import operation_template
from qtgqlcodegen.compiler.template import OperationTemplateContext
from qtgqlcodegen.compiler.template import schema_types_template
from qtgqlcodegen.compiler.template import SchemaTemplateContext
from qtgqlcodegen.exceptions import QtGqlException
from qtgqlcodegen.graphql_ref import is_enum_definition
from qtgqlcodegen.graphql_ref import is_input_definition
from qtgqlcodegen.graphql_ref import is_interface_definition
from qtgqlcodegen.graphql_ref import is_list_definition
from qtgqlcodegen.graphql_ref import is_named_type_node
from qtgqlcodegen.graphql_ref import is_non_null_definition
from qtgqlcodegen.graphql_ref import is_nonnull_node
from qtgqlcodegen.graphql_ref import is_object_definition
from qtgqlcodegen.graphql_ref import is_operation_def_node
from qtgqlcodegen.graphql_ref import is_scalar_definition
from qtgqlcodegen.graphql_ref import is_union_definition
from qtgqlcodegen.objecttype import EnumMap
from qtgqlcodegen.objecttype import EnumValue
from qtgqlcodegen.objecttype import GqlTypeHinter
from qtgqlcodegen.objecttype import QtGqlEnumDefinition
from qtgqlcodegen.objecttype import QtGqlFieldDefinition
from qtgqlcodegen.objecttype import QtGqlInputFieldDefinition
from qtgqlcodegen.objecttype import QtGqlInputObjectTypeDefinition
from qtgqlcodegen.objecttype import QtGqlInterfaceDefinition
from qtgqlcodegen.objecttype import QtGqlObjectTypeDefinition
from qtgqlcodegen.objecttype import QtGqlVariableDefinition
from qtgqlcodegen.utils import anti_forward_ref
from qtgqlcodegen.utils import FileSpec

if TYPE_CHECKING:  # pragma: no cover
    from qtgqlcodegen.config import QtGqlConfig

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
        self.operations: dict[str, QtGqlOperationDefinition] = {}
        self.evaluator = evaluator

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
            if operation.operation in (
                OperationType.QUERY,
                OperationType.MUTATION,
                OperationType.SUBSCRIPTION,
            ):
                assert operation.name, "QtGql enforces operations to have names."
                operation_vars: list[QtGqlVariableDefinition] = []

                # input variables
                if variables_def := operation.variable_definitions:
                    for var in variables_def:
                        operation_vars.append(self._parse_variable_definition(var))

                operation_definition = QtGqlOperationDefinition.from_definition(
                    operation_def=operation,
                    evaluator=self.evaluator,
                    directives=node.directives,
                    variables=operation_vars,
                )
                self.operations[operation_definition.name] = operation_definition


class SchemaEvaluator:
    def __init__(self, config: QtGqlConfig):
        self.config = config
        self._objecttypes_def_map: dict[str, QtGqlObjectTypeDefinition] = {}
        self._enums_def_map: EnumMap = {}
        self._input_objects_def_map: dict[str, QtGqlInputObjectTypeDefinition] = {}
        self._interfaces_map: dict[str, QtGqlInterfaceDefinition] = {}
        self._operations: dict[str, QtGqlOperationDefinition] = {}
        self.operation_types: dict[OperationType, QtGqlObjectTypeDefinition] = {}

    def get_interface_by_name(self, name: str) -> Optional[QtGqlInterfaceDefinition]:
        return self._interfaces_map.get(name, None)

    def get_objecttype_by_name(self, name: str) -> Optional[QtGqlObjectTypeDefinition]:
        return self._objecttypes_def_map.get(name, None)

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
        return graphql.build_schema(
            (self.config.graphql_dir / "schema.graphql").resolve(True).read_text(),
        )

    @cached_property
    def root_types(self) -> List[Optional[gql_def.GraphQLObjectType]]:
        return [
            self.schema_definition.get_root_type(OperationType.QUERY),
            self.schema_definition.get_root_type(OperationType.MUTATION),
            self.schema_definition.get_root_type(OperationType.SUBSCRIPTION),
        ]

    @cached_property
    def root_types_names(self) -> str:
        return " ".join([tp.name for tp in self.root_types if tp])

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
            ret = GqlTypeHinter(
                type=list,
                of_type=(self._evaluate_field_type(list_def.of_type),),
                scalars=self.config.custom_scalars,
            )
        elif scalar_def := is_scalar_definition(t):
            if builtin_scalar := BuiltinScalars.by_graphql_name(scalar_def.name):
                ret = GqlTypeHinter(type=builtin_scalar, scalars=self.config.custom_scalars)
            else:
                ret = GqlTypeHinter(
                    type=self.config.custom_scalars[scalar_def.name],
                    scalars=self.config.custom_scalars,
                )
        elif enum_def := is_enum_definition(t):
            ret = GqlTypeHinter(
                type=anti_forward_ref(name=enum_def.name, type_map=self._enums_def_map),
                scalars=self.config.custom_scalars,
            )
        elif obj_def := is_object_definition(t):
            ret = GqlTypeHinter(
                type=anti_forward_ref(name=obj_def.name, type_map=self._objecttypes_def_map),
                scalars=self.config.custom_scalars,
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
                        scalars=self.config.custom_scalars,
                    )
                    for possible in self.schema_definition.get_possible_types(union_def)
                ),
                scalars=self.config.custom_scalars,
            )
        elif input_def := is_input_definition(t):
            concrete = self.schema_definition.get_type(input_def.name)
            assert isinstance(concrete, gql_def.GraphQLInputObjectType)
            ret = GqlTypeHinter(
                type=self._evaluate_input_type(input_def),
                scalars=self.config.custom_scalars,
            )

        elif interface_def := is_interface_definition(t):
            ret = GqlTypeHinter(
                type=self._evaluate_interface_type(interface_def),
                of_type=(),
                scalars=self.config.custom_scalars,
            )
        if not ret:  # pragma: no cover
            raise NotImplementedError(f"type {t} not supported yet")

        if is_optional:
            return GqlTypeHinter(type=Optional, of_type=(ret,), scalars=self.config.custom_scalars)
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
        if type_.name not in self.root_types_names:
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
        implements = [self._evaluate_interface_type(interface) for interface in type_.interfaces]

        ret = QtGqlObjectTypeDefinition(
            name=t_name,
            implements=implements,
            docstring=type_.description,
            fields_dict={
                name: self._evaluate_field(name, field) for name, field in type_.fields.items()
            },
        )
        self._objecttypes_def_map[ret.name] = ret
        for interface in type_.interfaces:
            qtgql_interface = self._evaluate_interface_type(interface)
            qtgql_interface.implementations[type_.name] = ret
        return ret

    def _evaluate_input_type(
        self,
        type_: gql_def.GraphQLInputObjectType,
    ) -> QtGqlInputObjectTypeDefinition:
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

    def _evaluate_interface_type(
        self,
        interface: gql_def.GraphQLInterfaceType,
    ) -> QtGqlInterfaceDefinition:
        if ret := self._interfaces_map.get(interface.name, None):
            return ret
        implements = [self._evaluate_interface_type(base) for base in interface.interfaces]
        ret = QtGqlInterfaceDefinition(
            name=interface.name,
            implements=implements,
            docstring=interface.description,
            fields_dict={
                name: self._evaluate_field(name, field) for name, field in interface.fields.items()
            },
        )
        self._interfaces_map[ret.name] = ret
        return ret

    def _evaluate_enum(self, enum: gql_def.GraphQLEnumType) -> Optional[QtGqlEnumDefinition]:
        name: str = enum.name

        if definition := self._enums_def_map.get(name, None):
            return definition

        ret = QtGqlEnumDefinition(
            name=name,
            members=[
                EnumValue(name=name, description=val.description or "")
                for name, val in enum.values.items()
            ],
        )

        self._enums_def_map[name] = ret
        return ret

    def parse_schema_concretes(self) -> None:
        for name, type_ in self.schema_definition.type_map.items():
            if name.startswith("__"):
                continue
            if object_definition := is_object_definition(type_):
                if object_type := self._evaluate_object_type(object_definition):
                    if object_definition is self.schema_definition.query_type:
                        self.operation_types[OperationType.QUERY] = object_type
                    elif object_definition is self.schema_definition.mutation_type:
                        self.operation_types[OperationType.MUTATION] = object_type
                    elif object_definition is self.schema_definition.subscription_type:
                        self.operation_types[OperationType.SUBSCRIPTION] = object_type

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
        self._operations.update(operation_miner.operations)

    def generate(self) -> list[FileSpec]:
        self.parse_schema_concretes()
        self.parse_operations()
        context = SchemaTemplateContext(
            enums=list(self._enums_def_map.values()),
            types=[
                t
                for name, t in self._objecttypes_def_map.items()
                if name not in BuiltinScalars.keys() and name not in self.root_types_names
            ],
            interfaces=list(self._interfaces_map.values()),
            input_objects=list(self._input_objects_def_map.values()),
            config=self.config,
        )

        operations: list[FileSpec] = []
        for op_name, op in self._operations.items():
            operations.append(
                FileSpec(
                    content=operation_template(
                        OperationTemplateContext(
                            operation=op,
                            config=self.config,
                        ),
                    ),
                    path=self.config.generated_dir / f"{op_name}.hpp",
                ),
            )
        schema = FileSpec(
            content=schema_types_template(context),
            path=self.config.generated_dir / "schema.hpp",
        )

        return [schema, *operations]

    def dump(self):
        """:param file: Path to the directory the codegen would dump to."""
        headers = self.generate()

        args = ["clang-format"] + [
            str(f.path) for f in headers if f.path.suffix in (".cpp", ".h", ".hpp")
        ]
        cmake = FileSpec(
            content=cmake_template(CmakeTemplateContext(config=self.config, sources=headers)),
            path=self.config.generated_dir / "CMakeLists.txt",
        )
        headers.append(cmake)
        args.append("-i")
        for f in headers:
            f.dump()
        subprocess.run(args)
