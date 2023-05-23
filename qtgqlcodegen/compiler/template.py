from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define
from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape

if TYPE_CHECKING:  # pragma: no cover
    from qtgqlcodegen.config import QtGqlConfig
    from qtgqlcodegen.compiler.operation import QtGqlOperationDefinition, QtGqlQueriedField
    from qtgqlcodegen.utils import FileSpec
    from qtgqlcodegen.objecttype import (
        QtGqlEnumDefinition,
        QtGqlInputObjectTypeDefinition,
        QtGqlInterfaceDefinition,
        QtGqlObjectTypeDefinition,
    )


template_env = Environment(
    loader=PackageLoader("qtgqlcodegen"),
    autoescape=select_autoescape(),
    variable_start_string="👉",  # originally {{ variable }}, using 👉 variable 👈 because C++ uses curly brackets.
    variable_end_string="👈",
)


def wrap_curly_filter(v: str, ignore: bool = False) -> str:
    if ignore:
        return v
    return "{" + v + "}"


template_env.filters["wrapcurly"] = wrap_curly_filter

SCHEMA_TEMPLATE = template_env.get_template("schema.jinja.hpp")
OPERATION_TEMPLATE = template_env.get_template("operation.jinja.hpp")
CONFIG_TEMPLATE = template_env.get_template("config.jinja.hpp")
CMAKE_TEMPLATE = template_env.get_template("CMakeLists.jinja.cmake")


@define
class SchemaTemplateContext:
    enums: list[QtGqlEnumDefinition]
    types: list[QtGqlObjectTypeDefinition]
    interfaces: list[QtGqlInterfaceDefinition]
    input_objects: list[QtGqlInputObjectTypeDefinition]
    config: QtGqlConfig

    @property
    def dependencies(self) -> list[str]:
        return [f"#include {scalar.include_path}" for scalar in self.config.custom_scalars.values()]

    @property
    def custom_scalars(self) -> list[str]:
        return [scalar.graphql_name for scalar in self.config.custom_scalars.values()]


@define(slots=False)
class OperationTemplateContext:
    operation: QtGqlOperationDefinition
    config: QtGqlConfig

    @property
    def ns(self) -> str:
        return self.operation.name.lower()

    @property
    def schema_ns(self) -> str:
        return self.config.env_name


def schema_types_template(context: SchemaTemplateContext) -> str:
    return SCHEMA_TEMPLATE.render(context=context)


def operation_template(context: OperationTemplateContext) -> str:
    return OPERATION_TEMPLATE.render(context=context)


@define(slots=False)
class CmakeTemplateContext:
    config: QtGqlConfig
    sources: list[FileSpec]

    @property
    def target_name(self) -> str:
        return self.config.env_name


def cmake_template(context: SchemaTemplateContext) -> str:
    return CMAKE_TEMPLATE.render(context=context)


@define
class ConfigContext:
    p_field: QtGqlQueriedField

    @property
    def choices(self):
        if self.p_field.choices:
            return {
                type_name: {
                    selection.name: selection.as_conf_string() or "None" for selection in selections
                }
                for type_name, selections in self.p_field.choices.items()
            }
        else:
            return {}

    @property
    def selections(self) -> dict[str, str]:
        if self.p_field.selections:
            return {
                selection.name: selection.as_conf_string()
                for selection in self.p_field.selections.values()
            }
        else:
            return {}


def config_template(context: ConfigContext):
    return CONFIG_TEMPLATE.render(context=context)
