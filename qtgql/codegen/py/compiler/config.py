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

    graphql_dir: Path
    """A directory contains [schema.graphql, query.graphql, mutation.graphql,
    subscription.graphql] generated types come from the schema.

    and queries, mutations, subscription handlers would be generated
    from the corresponding `.graphql` files.
    """
    env_name: str = "QGqlEnv"
    """The generated types would find the environment by this name.

    Also the generated QML imports would fall under this namespace.
    """
    evaluator: Type[SchemaEvaluator] = SchemaEvaluator
    """evaluates the schema and generates types."""
    custom_scalars: CustomScalarMap = CUSTOM_SCALARS
    """mapping of custom scalars, respected by the schema evaluator."""
    template_class: Callable[[TemplateContext], str] = py_template
    """jinja template."""
    base_object: Type[_BaseQGraphQLObject] = BaseGraphQLObject
    """base object to be extended by all generated types."""

    def fetch(self) -> None:
        res = requests.post(self.url, json={"query": introspection_query})
        introspected = res.json()["data"]
        self.evaluator.from_dict(introspected, config=self).dump(self.output)

    def __attrs_post_init__(self):
        if self.custom_scalars != CUSTOM_SCALARS:
            self.custom_scalars.update(CUSTOM_SCALARS)
