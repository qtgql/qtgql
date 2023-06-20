from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any

import jinja2
from attrs import define
from jinja2 import Environment, PackageLoader, select_autoescape

if TYPE_CHECKING:  # pragma: no cover
    from qtgqlcodegen.config import QtGqlConfig
    from qtgqlcodegen.utils import FileSpec

template_env = Environment(
    loader=PackageLoader("qtgqlcodegen"),
    autoescape=select_autoescape(),
    variable_start_string="👉",  # originally {{ variable }}, using 👉 variable 👈 because C++ uses curly brackets.
    variable_end_string="👈",
    undefined=jinja2.StrictUndefined,
)


def debug_jinja(obj: Any) -> None:  # pragma: no cover
    warnings.warn("jinja debug is called", stacklevel=2)
    return obj


template_env.globals.update(debug_jinja=debug_jinja)

CMAKE_TEMPLATE = template_env.get_template("CMakeLists.jinja.cmake")


@define(slots=False)
class CmakeTemplateContext:
    config: QtGqlConfig
    sources: list[FileSpec]

    @property
    def target_name(self) -> str:
        return self.config.env_name


def cmake_template(context: CmakeTemplateContext) -> str:
    return CMAKE_TEMPLATE.render(context=context)
