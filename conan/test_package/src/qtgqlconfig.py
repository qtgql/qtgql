from pathlib import Path

from qtgqlcodegen.config import QtGqlConfig

config = QtGqlConfig(
    env_name="example",
    graphql_dir=Path(__file__).parent / "graphql",
)
