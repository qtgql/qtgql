from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any

import jinja2
from attrs import define
from jinja2 import Environment, PackageLoader, select_autoescape

if TYPE_CHECKING:  # pragma: no cover
    from qtgqlcodegen.config import QtGqlConfig
    from qtgqlcodegen.generator import GenerationOutput
    from qtgqlcodegen.operation.definitions import QtGqlQueriedField

template_env: Environment = Environment(
    loader=PackageLoader("qtgqlcodegen"),
    autoescape=select_autoescape(),
    variable_start_string="👉",  # originally {{ variable }}, using 👉 variable 👈 because C++ uses curly brackets.
    variable_end_string="👈",
    undefined=jinja2.StrictUndefined,
)


def debug_jinja(obj: Any) -> None:  # pragma: no cover
    warnings.warn("jinja debug is called", stacklevel=2)
    return obj


class TemplatesLogic:
    """Some conditions are too complex to reside in the template.

    they will exist here and the templates would call them.
    """

    @staticmethod
    def field_might_not_exists_on_update(field: QtGqlQueriedField) -> bool:
        """This is used when updating a concrete field. Some fields are not
        "update-able" or we just deserialize them instead of update.

        This method would determine the needed behaviour.
        """
        f_concrete_type = field.concrete.type

        # concrete model fields currently doesn't update rather we just always deserialize the whole list and
        # proxies would update themselves correspondingly.
        if model := f_concrete_type.is_model:
            return model.needs_proxy_model

        # Root fields that has no default value might not have value even if
        # they are not optional.
        elif field.is_root:
            return True

        return False


template_env.globals.update(debug_jinja=debug_jinja)
template_env.globals.update(TemplatesLogic=TemplatesLogic())

CMAKE_TEMPLATE = template_env.get_template("CMakeLists.jinja.cmake")


@define(slots=False)
class CmakeTemplateContext:
    config: QtGqlConfig
    generation_output: GenerationOutput

    @property
    def target_name(self) -> str:
        return self.config.env_name


def cmake_template(context: CmakeTemplateContext) -> str:
    return CMAKE_TEMPLATE.render(context=context)
