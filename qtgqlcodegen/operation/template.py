from __future__ import annotations

from typing import TYPE_CHECKING

from attr import define

from qtgqlcodegen.core.template import template_env

if TYPE_CHECKING:
    from qtgqlcodegen.config import QtGqlConfig
    from qtgqlcodegen.operation.definitions import QtGqlOperationDefinition, QtGqlQueriedField
    from qtgqlcodegen.types import QtGqlInterfaceDefinition


@define(slots=False)
class OperationTemplateContext:
    operation: QtGqlOperationDefinition
    interfaces: list[QtGqlInterfaceDefinition]
    config: QtGqlConfig
    debug: bool = False

    @property
    def ns(self) -> str:
        return self.operation.name.lower()

    @property
    def schema_ns(self) -> str:
        return self.config.env_name


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


OPERATION_HPP_TEMPLATE = template_env.get_template("operation.jinja.hpp")
OPERATION_CPP_TEMPLATE = template_env.get_template("operation.jinja.cpp")
CONFIG_TEMPLATE = template_env.get_template("config.jinja.hpp")
