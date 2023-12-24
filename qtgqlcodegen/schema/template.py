from __future__ import annotations

from typing import TYPE_CHECKING

from attr import define

from qtgqlcodegen.core.template import template_env
from qtgqlcodegen.operation.template import (
    OPERATION_CPP_TEMPLATE,
    OPERATION_HPP_TEMPLATE,
    OperationTemplateContext,
)

if TYPE_CHECKING:
    from qtgqlcodegen.config import QtGqlConfig
    from qtgqlcodegen.types import (
        QtGqlEnumDefinition,
        QtGqlInputObject,
        QtGqlInterface,
        QtGqlObjectType,
    )


@define
class SchemaTemplateContext:
    enums: list[QtGqlEnumDefinition]
    types: list[QtGqlObjectType]
    interfaces: list[QtGqlInterface]
    input_objects: list[QtGqlInputObject]
    config: QtGqlConfig

    @property
    def dependencies(self) -> list[str]:
        ret: list[str] = []
        for scalar in self.config.custom_scalars.values():
            include_path = scalar.include_path
            if include_path not in ret:
                if not (include_path.startswith(('"', "<"))):
                    include_path = f'"{include_path}"'
                ret.append(include_path)
        return [f"#include {inc}" for inc in ret]

    @property
    def custom_scalars(self) -> list[str]:
        return [scalar.graphql_name for scalar in self.config.custom_scalars.values()]

    @property
    def export_macro(self) -> str:
        return f"QTGQL_{self.config.env_name}_SCHEMA_EXPORT"


def schema_types_template_hpp(context: SchemaTemplateContext) -> str:
    return SCHEMA_HPP_TEMPLATE.render(context=context)


def operation_hpp_template(context: OperationTemplateContext) -> str:
    return OPERATION_HPP_TEMPLATE.render(context=context)


def operation_cpp_template(context: OperationTemplateContext) -> str:
    return OPERATION_CPP_TEMPLATE.render(context=context)


SCHEMA_HPP_TEMPLATE = template_env.get_template("schema.jinja.hpp")
