from functools import cached_property
from pathlib import Path
from typing import Callable
from typing import Type

from attrs import define

from qtgqlcodegen.compiler.template import schema_types_template
from qtgqlcodegen.compiler.template import SchemaTemplateContext
from qtgqlcodegen.introspection import SchemaEvaluator
from qtgqlcodegen.runtime.custom_scalars import CUSTOM_SCALARS
from qtgqlcodegen.runtime.custom_scalars import CustomScalarMap


@define(slots=False)
class QtGqlConfig:
    """Encapsulates configurations for a qtgql-codegen application per GraphQL
    schema."""

    graphql_dir: Path
    """A directory contains.

    - schema.graphql, represents the current schema definition at the server.
    - operations.graphql, queries, mutations and subscription handlers would be generated based on the operations defined there.
    """
    env_name: str = "QGqlEnv"
    """The generated types would find the environment by this name.

    Also the generated QML imports would fall under this namespace.
    """
    evaluator: Type[SchemaEvaluator] = SchemaEvaluator
    """evaluates the schema and generates types."""
    custom_scalars: CustomScalarMap = {}
    """mapping of custom scalars, respected by the schema evaluator."""
    template_class: Callable[[SchemaTemplateContext], str] = schema_types_template
    """jinja template."""

    @cached_property
    def schema_path(self) -> Path:
        return self.graphql_dir / "schema.graphql"

    @cached_property
    def operations_dir(self) -> Path:
        return self.graphql_dir / "operations.graphql"

    @cached_property
    def generated_dir(self):
        ret = self.graphql_dir / "__generated__"
        if not ret.exists():
            ret.mkdir()
        return ret

    @cached_property
    def _evaluator(self) -> SchemaEvaluator:
        return self.evaluator(self)

    def generate(self) -> None:
        self._evaluator.dump()

    def __attrs_post_init__(self):
        if self.custom_scalars != CUSTOM_SCALARS:
            self.custom_scalars.update(CUSTOM_SCALARS)
