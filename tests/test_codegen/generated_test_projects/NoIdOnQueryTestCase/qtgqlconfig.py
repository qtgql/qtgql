from pathlib import Path

from qtgqlcodegen.config import QtGqlConfig

config = QtGqlConfig(
    graphql_dir=Path(
        "/home/nir/Desktop/tzv5hob/qtgql/tests/test_codegen/generated_test_projects/NoIdOnQueryTestCase/graphql",
    ),
    env_name="NoIdOnQueryTestCase",
)