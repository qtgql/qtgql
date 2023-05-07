from pathlib import Path

from qtgqlcodegen.config import QtGqlConfig

config = QtGqlConfig(
    graphql_dir=Path("{{context.config.graphql_dir}}"),
    env_name="{{context.config.env_name}}",
)
