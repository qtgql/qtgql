from __future__ import annotations

import contextlib
import enum
from functools import cached_property
from typing import Any, Optional, Type

from attrs import define

from qtgql.codegen.py.compiler.builtin_scalars import BuiltinScalar
from qtgql.codegen.py.runtime.bases import QGraphQListModel
from qtgql.codegen.py.runtime.custom_scalars import BaseCustomScalar, CustomScalarMap
from qtgql.codegen.utils import AntiForwardRef
from qtgql.utils.typingref import TypeHinter


class Kinds(enum.Enum):
    SCALAR = "SCALAR"
    OBJECT = "OBJECT"
    ENUM = "ENUM"
    LIST = "LIST"
    UNION = "UNION"
    NON_NULL = "NON_NULL"
    INTERFACE = "INTERFACE"
    INPUT_OBJECT = "INPUT_OBJECT"


@define(slots=False)
class GqlFieldDefinition:
    name: str
    type: GqlTypeHinter
    type_map: dict[str, GqlTypeDefinition]
    enums: EnumMap
    scalars: CustomScalarMap
    description: Optional[str] = ""

    @cached_property
    def default_value(self):
        if builtin_scalar := self.type.is_builtin_scalar:
            if builtin_scalar.tp is str:
                return f"'{builtin_scalar.default_value}'"
            return f"{builtin_scalar.default_value}"
        if self.type.is_object_type:
            return "None"

        if self.type.is_model:
            # this would just generate the model without data.
            return "list()"

        if custom_scalar := self.type.is_custom_scalar(self.scalars):
            return f"SCALARS.{custom_scalar.__name__}()"

        if enum_def := self.type.is_enum:
            return f"{enum_def.name}(1)"  # 1 is where auto() starts.

        return "None"  # Unions are not supported yet.

    @property
    def is_custom_scalar(self) -> Optional[Type[BaseCustomScalar]]:
        return self.type.is_custom_scalar(self.scalars)

    @cached_property
    def annotation(self) -> str:
        """
        :returns: Annotation of the field based on the real type,
        meaning that the private attribute would be of that type.
        this goes for init and the property setter.
        """
        return self.type.annotation(self.scalars)

    @cached_property
    def fget_annotation(self) -> str:
        """This annotates the value that is QML-compatible."""
        if custom_scalar := self.type.is_custom_scalar(self.scalars):
            return TypeHinter.from_annotations(
                custom_scalar.to_qt.__annotations__["return"]
            ).stringify()
        if self.type.is_enum:
            return "int"

        return self.annotation

    @cached_property
    def property_type(self) -> str:
        try:
            # this should raise if it is an inner type.
            ret = GqlTypeHinter.from_string(self.fget_annotation, self.type_map)
            if ret.type in self.type_map.values():
                raise TypeError  # in py3.11 the get_type_hints won't explicitly raise.
            return self.fget_annotation
        except (TypeError, NameError):
            if self.type.is_union():
                # graphql doesn't support scalars in Unions ATM. (what about Enums in unions)?
                return "QObject"
            if self.type.is_enum:
                # QEnum value must be int
                return "int"
            # might be a model, which is also QObject
            assert self.type.is_model or self.type.is_object_type
            return "QObject"

    @cached_property
    def setter_name(self) -> str:
        return self.name + "_setter"

    @cached_property
    def signal_name(self) -> str:
        return self.name + "Changed"

    @cached_property
    def private_name(self) -> str:
        return "_" + self.name

    @property
    def fget(self) -> str:
        if self.type.is_custom_scalar(self.scalars):
            return f"return self.{self.private_name}.{BaseCustomScalar.to_qt.__name__}()"
        if self.type.is_enum:
            return f"return self.{self.private_name}.value"
        return f"return self.{self.private_name}"

    @cached_property
    def can_select_id(self) -> Optional[GqlFieldDefinition]:
        object_type = self.type.is_object_type or self.type.is_model
        if object_type:
            return object_type.has_id_field


@define(slots=False)
class GqlTypeDefinition:
    name: str
    fields_dict: dict[str, GqlFieldDefinition]
    docstring: Optional[str] = ""

    @cached_property
    def has_id_field(self) -> Optional[GqlFieldDefinition]:
        return self.fields_dict.get("id", None)

    @cached_property
    def id_is_optional(self) -> Optional[GqlFieldDefinition]:
        if id_f := self.has_id_field:
            if id_f.type.is_optional():
                return id_f

    @property
    def fields(self) -> list[GqlFieldDefinition]:
        return list(self.fields_dict.values())


@define
class EnumValue:
    """encapsulates enumValues from introspection, maps to an Enum member."""

    name: str
    description: str = ""


@define
class GqlEnumDefinition:
    name: str
    members: list[EnumValue]


EnumMap = dict[str, "GqlEnumDefinition"]


def optional_maybe(th: GqlTypeHinter) -> GqlTypeHinter:
    return th if not th.is_optional() else th.of_type[0]


class GqlTypeHinter(TypeHinter):
    def __init__(
        self,
        type: Any,
        of_type: tuple[GqlTypeHinter, ...] = (),
    ):
        self.type = type
        self.of_type: tuple[GqlTypeHinter, ...] = of_type

    @property
    def is_object_type(self) -> Optional[GqlTypeDefinition]:
        t_self = optional_maybe(self).type
        with contextlib.suppress(TypeError):
            if issubclass(t_self, AntiForwardRef):
                ret = t_self.resolve()
                if isinstance(ret, GqlTypeDefinition):
                    return ret

    @property
    def is_model(self) -> Optional[GqlTypeDefinition]:
        t_self = optional_maybe(self)
        if t_self.is_list():
            # enums and scalars or unions are not supported in lists yet (valid graphql spec though)
            return t_self.of_type[0].is_object_type

    @property
    def is_enum(self) -> Optional[GqlEnumDefinition]:
        t_self = optional_maybe(self).type
        with contextlib.suppress(TypeError):
            if issubclass(t_self, AntiForwardRef):
                if isinstance(t_self.resolve(), GqlEnumDefinition):
                    return t_self.resolve()

    @property
    def is_builtin_scalar(self) -> Optional[BuiltinScalar]:
        t_self = optional_maybe(self).type
        if isinstance(t_self, BuiltinScalar):
            return t_self

    def is_custom_scalar(self, scalars: CustomScalarMap) -> Optional[Type[BaseCustomScalar]]:
        t_self = optional_maybe(self).type
        if t_self in scalars.values():
            return t_self

    def annotation(self, scalars: CustomScalarMap) -> str:
        """
        :returns: Annotation of the field based on the real type,
        meaning that the private attribute would be of that type.
        this goes for init and the property setter. They are optional by default,
        (at the template) so unwrap optional first
        """
        t_self = optional_maybe(self)

        # int, str, float etc...
        if builtin_scalar := t_self.is_builtin_scalar:
            return builtin_scalar.tp.__name__

        if scalar := t_self.is_custom_scalar(scalars):
            return f"SCALARS.{scalar.__name__}"
        if gql_enum := t_self.is_enum:
            return gql_enum.name
        # handle Optional, Union, List etc...
        # removing redundant prefixes.
        if model_of := t_self.is_model:
            return f"{QGraphQListModel.__name__}[{model_of.name}]"
        if object_def := t_self.is_object_type:
            return f"Optional[{object_def.name}]"
        if t_self.is_union():
            return "Union[" + ",".join(th.annotation(scalars) for th in t_self.of_type) + "]"
        raise NotImplementedError  # pragma no cover

    def as_annotation(self, object_map=None):  # pragma: no cover
        raise NotImplementedError("not safe to call on this type")
