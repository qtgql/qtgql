from pathlib import Path
from typing import Callable, Type

import requests  # type: ignore
from attrs import define

from qtgql.codegen.introspection import SchemaEvaluator, introspection_query
from qtgql.codegen.py.compiler.template import TemplateContext, py_template
from qtgql.codegen.py.runtime.bases import BaseGraphQLObject, _BaseQGraphQLObject
from qtgql.codegen.py.runtime.custom_scalars import CUSTOM_SCALARS, CustomScalarMap


@define
class QtGqlConfig:
    """Encapsulates configurations for a qtgql-codegen application per GraphQL
    schema."""

    url: str
    output: Path
    """full path for the generated output file."""
    evaluator: Type[SchemaEvaluator] = SchemaEvaluator
    """evaluates the schema and generates types."""
    custom_scalars: CustomScalarMap = CUSTOM_SCALARS
    """mapping of custom scalars, respected by the schema evaluator."""
    template_class: Callable[[TemplateContext], str] = py_template
    """jinja template."""
    base_object: Type[_BaseQGraphQLObject] = BaseGraphQLObject
    """base object to be extended by all generated types."""
    qml_import_name: str = "QtGql"
    """QMl generated imports would be under this namespace."""
    qml_dir: Path = Path.cwd()
    """Will be used to search qml files for queries, mutations, subscriptions
    and fragments."""
    env_name: str = "DEFAULT"
    """The generated environment would be found in env_map under this name."""

    def fetch(self) -> None:
        res = requests.post(self.url, json={"query": introspection_query})
        introspected = res.json()["data"]
        self.evaluator.from_dict(introspected, config=self).dump(self.output)

    def __attrs_post_init__(self):
        if self.custom_scalars != CUSTOM_SCALARS:
            self.custom_scalars.update(CUSTOM_SCALARS)
