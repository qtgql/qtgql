from __future__ import annotations

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


def wrap_curly_filter(v: str, ignore: bool = False) -> str:
    if ignore:
        return v
    return "{" + v + "}"


def debug(obj: Any):  # pragma: no cover
    print(obj)  # noqa


template_env.filters["wrapcurly"] = wrap_curly_filter
template_env.globals.update(debug=debug)

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
