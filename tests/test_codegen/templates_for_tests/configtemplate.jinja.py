from pathlib import Path

from qtgqlcodegen.config import QtGqlConfig

config = QtGqlConfig(
    graphql_dir=Path(r"👉 context.config.graphql_dir 👈"),
    env_name="👉 context.config.env_name 👈",
    generated_dir_name="../gen",
    qml_plugins_path="👉 context.config.qml_plugins_path 👈",
)
