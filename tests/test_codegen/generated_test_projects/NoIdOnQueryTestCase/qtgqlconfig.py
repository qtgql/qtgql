from pathlib import Path

from qtgqlcodegen.config import QtGqlConfig

config = QtGqlConfig(
    graphql_dir=Path(
        r"C:\Users\temp\Desktop\clones\qtgql\tests\test_codegen\generated_test_projects\NoIdOnQueryTestCase\graphql",
    ),
    env_name="NoIdOnQueryTestCase",
)
