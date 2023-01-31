from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

import graphql

from qtgql.codegen.py.compiler import TemplateContext
from qtgql.codegen.py.objecttype import FieldProperty, GqlType, Kinds
from qtgql.codegen.py.scalars import CUSTOM_SCALARS, BuiltinScalars
from qtgql.codegen.utils import anti_forward_ref
from qtgql.typingref import TypeHinter

if TYPE_CHECKING:
    from qtgql.codegen.py.config import QtGqlConfig

introspection_query = graphql.get_introspection_query(descriptions=True)


class SchemaEvaluator:
    def __init__(self, introspection: dict, config: QtGqlConfig):
        self.template = config.template_class
        self.introspection = introspection
        self.config = config
        self._generated_types: dict[str, GqlType] = {
            scalar: GqlType(name=scalar, kind=Kinds.SCALAR, fields=[])
            for scalar in BuiltinScalars.keys()
        }
        self._evaluate()

    @cached_property
    def unions(self) -> list[dict]:
        return [
            t for t in self.introspection["__schema"]["types"] if Kinds[t["kind"]] == Kinds.UNION
        ]

    def get_possible_types_for_union(self, name: str) -> list[dict]:
        for union in self.unions:
            if union["name"] == name:
                return union["possibleTypes"]
        raise ValueError(f"Union for {name} was not found")

    def evaluate_field_type(self, t: dict) -> TypeHinter:
        kind = Kinds[t["kind"]]

        is_optional = True
        if kind == Kinds.NON_NULL:
            # move to inner, this is not optional
            t = t["ofType"]
            is_optional = False

        of_type = t["ofType"]
        name = t["name"]
        kind = Kinds[t["kind"]]
        ret: Optional[TypeHinter] = None

        def optional_maybe(inner: TypeHinter) -> TypeHinter:
            return TypeHinter(type=Optional, of_type=(inner,)) if is_optional else inner

        if kind == Kinds.LIST:
            ret = TypeHinter(type=list, of_type=(self.evaluate_field_type(of_type),))
        elif kind == Kinds.SCALAR:
            try:
                ret = TypeHinter(type=BuiltinScalars[name])
            except KeyError:
                ret = TypeHinter(type=CUSTOM_SCALARS[name])
        elif kind == Kinds.OBJECT:
            ret = TypeHinter(type=anti_forward_ref(name))
        elif kind == Kinds.UNION:
            ret = TypeHinter(
                type=Union,
                of_type=tuple(
                    TypeHinter(type=anti_forward_ref(possible["name"]))
                    for possible in self.get_possible_types_for_union(name)
                ),
            )
        if ret:
            return optional_maybe(ret)

        raise NotImplementedError(f"kind {kind} not supported yet")

    def evaluate_field(self, field: dict) -> FieldProperty:
        """we don't really know what is the field type just it's name."""
        return FieldProperty(
            type=self.evaluate_field_type(field["type"]),
            name=field["name"],
            type_map=self._generated_types,
            scalars=self.config.custom_scalars,
            description=field["description"],
        )

    def evaluate_object_type(self, type_: dict) -> Optional[GqlType]:
        # scalars are swallowed here.
        t_name: str = type_["name"]
        if t_name.startswith("__"):
            return None
        if evaluated := self._generated_types.get(t_name, None):
            return evaluated

        concrete = GqlType(
            kind=Kinds.OBJECT,
            name=t_name,
            docstring=type_["description"],
            fields=[self.evaluate_field(f) for f in type_["fields"]],
        )
        self._generated_types[t_name] = concrete
        return concrete

    def _evaluate(self) -> None:
        types = self.introspection["__schema"]["types"]
        for tp in types:
            kind = tp["kind"]
            if kind == Kinds.SCALAR.name:
                continue
            if kind == Kinds.OBJECT.name:
                self.evaluate_object_type(tp)

    def generate(self) -> str:
        """
        :return: The generated schema module as a string.
        """
        return self.template(
            TemplateContext(
                types=[
                    t
                    for name, t in self._generated_types.items()
                    if name not in BuiltinScalars.keys()
                ],
                config=self.config,
            )
        )

    @classmethod
    def from_dict(cls, introspection: dict, config: QtGqlConfig) -> SchemaEvaluator:
        evaluator = SchemaEvaluator(introspection, config=config)
        return evaluator

    def dump(self, file: Path):
        """
        :param file: Path to the file the codegen would dump to.
        """
        with open(file, "w") as fh:
            fh.write(self.generate())
