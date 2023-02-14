from __future__ import annotations

import glob
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, NewType, Optional, Union

import graphql
from graphql import OperationType, parse

from qtgql.codegen.py.compiler.builtin_scalars import BuiltinScalars
from qtgql.codegen.py.compiler.query import QueryHandlerDefinition, find_gql
from qtgql.codegen.py.compiler.template import TemplateContext
from qtgql.codegen.py.objecttype import (
    EnumMap,
    EnumValue,
    GqlEnumDefinition,
    GqlFieldDefinition,
    GqlTypeDefinition,
    GqlTypeHinter,
    Kinds,
)
from qtgql.codegen.utils import anti_forward_ref

if TYPE_CHECKING:  # pragma: no cover
    from qtgql.codegen.py.compiler.config import QtGqlConfig

introspection_query = graphql.get_introspection_query(descriptions=True)


OperationName = NewType("OperationName", str)


class SchemaEvaluator:
    def __init__(self, introspection: dict, config: QtGqlConfig):
        self.template = config.template_class
        self.introspection = introspection
        self.config = config
        self._generated_types: dict[str, GqlTypeDefinition] = {}
        self._generated_enums: EnumMap = {}
        self._fragments_store: dict[int, str] = {}
        self._query_handlers: dict[OperationName, QueryHandlerDefinition] = {}

    @cached_property
    def unions(self) -> list[dict]:
        return [
            t for t in self.introspection["__schema"]["types"] if Kinds(t["kind"]) == Kinds.UNION
        ]

    @property
    def query_type(self) -> GqlTypeDefinition:
        return self._generated_types[self.introspection["__schema"]["queryType"]["name"]]

    def get_possible_types_for_union(self, name: str) -> list[dict]:
        for union in self.unions:
            if union["name"] == name:
                return union["possibleTypes"]
        raise ValueError(f"Union for {name} was not found")  # pragma: no cover

    def _evaluate_field_type(self, t: dict) -> GqlTypeHinter:
        kind = Kinds(t["kind"])

        if kind == Kinds.NON_NULL:
            # There are no optionals in qtgql, we use default values.
            # By default, everything in graphql is optional,
            # so NON_NULL doesn't really make a difference,
            t = t["ofType"]

        of_type = t["ofType"]
        name = t["name"]
        kind = Kinds(t["kind"])
        ret: Optional[GqlTypeHinter] = None

        if kind == Kinds.LIST:
            ret = GqlTypeHinter(type=list, of_type=(self._evaluate_field_type(of_type),))
        elif kind == Kinds.SCALAR:
            if builtin_scalar := BuiltinScalars.by_graphql_name(name):
                ret = GqlTypeHinter(type=builtin_scalar)
            else:
                ret = GqlTypeHinter(type=self.config.custom_scalars[name])
        elif kind is Kinds.ENUM:
            ret = GqlTypeHinter(type=anti_forward_ref(name=name, type_map=self._generated_enums))
        elif kind is Kinds.OBJECT:
            ret = GqlTypeHinter(type=anti_forward_ref(name=name, type_map=self._generated_types))
        elif kind == Kinds.UNION:
            ret = GqlTypeHinter(
                type=Union,
                of_type=tuple(
                    GqlTypeHinter(
                        type=anti_forward_ref(name=possible["name"], type_map=self._generated_types)
                    )
                    for possible in self.get_possible_types_for_union(name)
                ),
            )
        if ret:
            return ret

        raise NotImplementedError(f"kind {kind} not supported yet")  # pragma: no cover

    def _evaluate_field(self, field: dict) -> GqlFieldDefinition:
        """we don't really know what is the field type just it's name."""
        return GqlFieldDefinition(
            type=self._evaluate_field_type(field["type"]),
            name=field["name"],
            type_map=self._generated_types,
            scalars=self.config.custom_scalars,
            description=field["description"],
            enums=self._generated_enums,
        )

    def _evaluate_object_type(self, type_: dict) -> Optional[GqlTypeDefinition]:
        # scalars are swallowed here.
        t_name: str = type_["name"]
        if t_name.startswith("__"):
            return None
        if evaluated := self._generated_types.get(t_name, None):
            return evaluated

        concrete = GqlTypeDefinition(
            kind=Kinds.OBJECT,
            name=t_name,
            docstring=type_["description"],
            fields=[self._evaluate_field(f) for f in type_["fields"]],
        )
        return concrete

    def _evaluate_enum(self, enum: dict) -> Optional[GqlEnumDefinition]:
        name: str = enum["name"]
        if name.startswith("__"):
            return None
        if self._generated_enums.get(name, None):
            return None

        return GqlEnumDefinition(
            name=name,
            members=[
                EnumValue(name=val["name"], description=val["description"])
                for val in enum["enumValues"]
            ],
        )

    def parse_schema_concretes(self) -> None:
        types = self.introspection["__schema"]["types"]
        for tp in types:
            kind = Kinds(tp["kind"])
            if kind is Kinds.SCALAR:
                continue
            elif kind is Kinds.OBJECT:
                if object_type := self._evaluate_object_type(tp):
                    self._generated_types[object_type.name] = object_type
            elif kind is Kinds.ENUM:
                if enum := self._evaluate_enum(tp):
                    self._generated_enums[enum.name] = enum

    def parse_qml_operations(self) -> None:
        qml_files = glob.glob(f"{str(self.config.qml_dir)}/**/*.qml", recursive=True)
        for relative in qml_files:
            file = self.config.qml_dir / relative
            with open(file) as f:
                for node in find_gql(f.read()):
                    ast = parse(node)
                    for definition in ast.definitions:
                        field_name = definition.selection_set.selections[0].name.value  # type: ignore
                        field = None
                        if definition.operation is OperationType.QUERY:  # type: ignore
                            for field_iml in self.query_type.fields:
                                if field_iml.name == field_name:
                                    field = field_iml
                            assert field
                            self._query_handlers[OperationName(node)] = QueryHandlerDefinition(
                                query=node,
                                name=definition.name.value,  # type: ignore
                                field=field,
                                directives=definition.directives,  # type: ignore
                            )

    def dumps(self) -> str:
        """:return: The generated schema module as a string."""
        self.parse_schema_concretes()
        self.parse_qml_operations()
        return self.template(
            TemplateContext(
                enums=list(self._generated_enums.values()),
                types=[
                    t
                    for name, t in self._generated_types.items()
                    if name not in BuiltinScalars.keys()
                ],
                queries=list(self._query_handlers.values()),
                config=self.config,
            )
        )

    @classmethod
    def from_dict(cls, introspection: dict, config: QtGqlConfig) -> SchemaEvaluator:
        evaluator = SchemaEvaluator(introspection, config=config)
        evaluator.parse_schema_concretes()
        return evaluator

    def dump(self, file: Path):
        """:param file: Path to the file the codegen would dump to."""
        with open(file, "w") as fh:
            fh.write(self.dumps())
