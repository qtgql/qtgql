from pathlib import Path
from typing import Type

import requests  # type: ignore
from attrs import define

from qtgql.codegen.introspection import SchemaEvaluator, introspection_query


@define
class QtGqlConfig:
    url: str
    output: Path
    """full path for the generated output file."""
    evaluator: Type[SchemaEvaluator] = SchemaEvaluator

    def fetch(self) -> None:
        res = requests.post(self.url, json={"query": introspection_query})
        introspected = res.json()["data"]
        self.evaluator.from_dict(introspected).dump(self.output)
