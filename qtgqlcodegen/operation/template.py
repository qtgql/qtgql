from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from attr import define

from qtgqlcodegen.core.cppref import QtGqlTypes
from qtgqlcodegen.core.template import template_env

if TYPE_CHECKING:
    from qtgqlcodegen.config import QtGqlConfig
    from qtgqlcodegen.operation.definitions import QtGqlOperationDefinition


@define(slots=False)
class OperationTemplateContext:
    operation: QtGqlOperationDefinition
    config: QtGqlConfig
    debug: bool = False
    qtgql_types: ClassVar[type[QtGqlTypes]] = QtGqlTypes

    @property
    def ns(self) -> str:
        return self.operation.name.lower()

    @property
    def schema_ns(self) -> str:
        return self.config.env_name


OPERATION_HPP_TEMPLATE = template_env.get_template("operation.jinja.hpp")
OPERATION_CPP_TEMPLATE = template_env.get_template("operation.jinja.cpp")
