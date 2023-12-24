from pathlib import Path

from qtgqlcodegen.config import QtGqlConfig
{% if context.config.custom_scalars -%}
from qtgqlcodegen.types import CustomScalarDefinition
{% endif -%}
custom_scalars: dict[str, CustomScalarDefinition] = {}
{% for cs in context.config.custom_scalars.values() %}
custom_scalars["👉 cs.graphql_name 👈"] = CustomScalarDefinition(
    name="👉 cs.name 👈",
    graphql_name="👉 cs.graphql_name 👈",
    to_qt_type="👉 cs.to_qt_type 👈",
    deserialized_type="👉 cs.deserialized_type 👈",
    include_path="👉 cs.include_path 👈",
)
{% endfor -%}

config = QtGqlConfig(
    graphql_dir=Path(r"👉 context.config.graphql_dir 👈"),
    env_name="👉 context.config.env_name 👈",
    generated_dir_name="../gen",
    custom_scalars=custom_scalars,
    qml_plugins_path="👉 context.config.qml_plugins_path 👈",
)
