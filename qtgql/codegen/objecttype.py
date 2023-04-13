from __future__ import annotations

import contextlib
import enum
from functools import cached_property
from typing import Any
from typing import Generic
from typing import Optional
from typing import Type
from typing import TypeVar

import attrs
from attrs import define
from typingref import TypeHinter
from typingref import UNSET

from qtgql.codegen.py.compiler.builtin_scalars import BuiltinScalar
from qtgql.codegen.py.runtime.bases import QGraphQListModel
from qtgql.codegen.py.runtime.custom_scalars import BaseCustomScalar
from qtgql.codegen.py.runtime.custom_scalars import CustomScalarMap
from qtgql.codegen.utils import AntiForwardRef


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
class QtGqlBaseTypedNode:
    name: str
    type: GqlTypeHinter
    type_map: dict[str, QtGqlObjectTypeDefinition]
    enums: EnumMap
    scalars: CustomScalarMap

    @cached_property
    def is_custom_scalar(self) -> Optional[Type[BaseCustomScalar]]:
        return self.type.is_custom_scalar

    @cached_property
    def annotation(self) -> str:
        """
        :returns: Annotation of the field based on the real type,
        meaning that the private attribute would be of that type.
        this goes for init and the property setter.
        """
        return self.type.annotation


T = TypeVar("T")


@define(slots=False)
class QtGqlVariableDefinition(Generic[T], QtGqlBaseTypedNode):
    default_value: Optional[T] = UNSET

    def json_repr(self, attr_name: Optional[str] = None) -> str:
        if not attr_name:
            attr_name = self.name
        if self.type.is_input_object_type:
            return f"{attr_name}.asdict()"
        elif self.type.is_builtin_scalar:
            return attr_name
        elif self.type.is_enum:
            return f"{attr_name}.name"
        elif self.is_custom_scalar:
            return f"{attr_name}.{BaseCustomScalar.parse_value.__name__}()"

        raise NotImplementedError(f"{self.type} is not supported as an input type ATM")


@define(slots=False)
class BaseQtGqlFieldDefinition(QtGqlBaseTypedNode):
    description: Optional[str] = ""


@define(slots=False)
class QtGqlInputFieldDefinition(BaseQtGqlFieldDefinition, QtGqlVariableDefinition):
    ...


@define(slots=False)
class QtGqlFieldDefinition(BaseQtGqlFieldDefinition):
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

        if custom_scalar := self.type.is_custom_scalar:
            return f"SCALARS.{custom_scalar.__name__}()"

        if enum_def := self.type.is_enum:
            return f"{enum_def.name}(1)"  # 1 is where auto() starts.

        return "None"  # Unions are not supported yet.

    @cached_property
    def fget_annotation(self) -> str:
        """This annotates the value that is QML-compatible."""
        if custom_scalar := self.type.is_custom_scalar:
            return TypeHinter.from_annotations(
                custom_scalar.to_qt.__annotations__["return"],
            ).stringify()
        if self.type.is_enum:
            return "int"

        return self.annotation

    @cached_property
    def property_type(self) -> str:
        if self.type.is_builtin_scalar or self.type.is_custom_scalar:
            return self.fget_annotation
        else:
            if self.type.is_enum:
                # QEnum value must be int
                return "int"
            # might be a model, which is also QObject
            # graphql doesn't support scalars or enums in Unions ATM.
            assert (
                self.type.is_model
                or self.type.is_object_type
                or self.type.is_interface
                or self.type.is_union
            )
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
        if self.type.is_custom_scalar:
            return f"return self.{self.private_name}.{BaseCustomScalar.to_qt.__name__}()"
        if self.type.is_enum:
            return f"return self.{self.private_name}.value"
        return f"return self.{self.private_name}"

    @cached_property
    def can_select_id(self) -> Optional[QtGqlFieldDefinition]:
        object_type = self.type.is_object_type or self.type.is_interface
        if not object_type:
            if self.type.is_model:
                object_type = self.type.is_model.is_object_type
        if object_type:
            return object_type.has_id_field


@define(slots=False)
class BaseGqlTypeDefinition:
    name: str
    fields_dict: dict[str, QtGqlFieldDefinition]
    docstring: Optional[str] = ""

    @property
    def fields(self) -> list[QtGqlFieldDefinition]:
        return list(self.fields_dict.values())


@define(slots=False)
class QtGqlObjectTypeDefinition(BaseGqlTypeDefinition):
    implements: list[QtGqlInterfaceDefinition] = attrs.Factory(list)

    @cached_property
    def has_id_field(self) -> Optional[QtGqlFieldDefinition]:
        return self.fields_dict.get("id", None)

    @cached_property
    def id_is_optional(self) -> Optional[QtGqlFieldDefinition]:
        if id_f := self.has_id_field:
            if id_f.type.is_optional():
                return id_f

    def __attrs_post_init__(self):
        for base in self.implements:
            if not base.implementations.get(self.name):
                base.implementations[self.name] = self


@define(slots=False)
class QtGqlInterfaceDefinition(QtGqlObjectTypeDefinition):
    implementations: dict[str, BaseGqlTypeDefinition] = attrs.field(factory=dict)


@define(slots=False)
class QtGqlInputObjectTypeDefinition(BaseGqlTypeDefinition):
    fields_dict: dict[str, QtGqlInputFieldDefinition] = attrs.field(factory=dict)  # type: ignore


@define
class EnumValue:
    """encapsulates enumValues from introspection, maps to an Enum member."""

    name: str
    description: str = ""


@define
class QtGqlEnumDefinition:
    name: str
    members: list[EnumValue]


EnumMap = dict[str, "QtGqlEnumDefinition"]


def freeze(self, key, value):  # pragma: no cover
    raise PermissionError("setattr called on frozen type")


class GqlTypeHinter(TypeHinter):
    def __init__(
        self,
        type: Any,
        scalars: CustomScalarMap,
        of_type: tuple[GqlTypeHinter, ...] = (),
    ):
        self.type = type
        self.of_type: tuple[GqlTypeHinter, ...] = of_type
        self.scalars = scalars
        self.__setattr__ = freeze  # type: ignore

    @cached_property
    def optional_maybe(self) -> GqlTypeHinter:
        return self if not super().is_optional() else self.of_type[0]

    @cached_property
    def is_union(self) -> bool:
        return super().is_union()

    @cached_property
    def is_object_type(self) -> Optional[QtGqlObjectTypeDefinition]:
        t_self = self.optional_maybe.type
        if self.is_interface:
            return None
        with contextlib.suppress(TypeError):
            if issubclass(t_self, AntiForwardRef):
                ret = t_self.resolve()
                if isinstance(ret, QtGqlObjectTypeDefinition):
                    return ret

    @cached_property
    def is_input_object_type(self) -> Optional[QtGqlInputObjectTypeDefinition]:
        t_self = self.optional_maybe.type
        if isinstance(t_self, QtGqlInputObjectTypeDefinition):
            return t_self

    @cached_property
    def is_model(self) -> Optional[GqlTypeHinter]:
        t_self = self.optional_maybe
        if t_self.is_list():
            # scalars or unions are not supported in lists yet (valid graphql spec though)
            return t_self.of_type[0]

    @cached_property
    def is_interface(self) -> Optional[QtGqlInterfaceDefinition]:
        t_self = self.optional_maybe.type
        if isinstance(t_self, QtGqlInterfaceDefinition):
            return t_self

    @cached_property
    def is_enum(self) -> Optional[QtGqlEnumDefinition]:
        t_self = self.optional_maybe.type
        with contextlib.suppress(TypeError):
            if issubclass(t_self, AntiForwardRef):
                if isinstance(t_self.resolve(), QtGqlEnumDefinition):
                    return t_self.resolve()

    @cached_property
    def is_builtin_scalar(self) -> Optional[BuiltinScalar]:
        t_self = self.optional_maybe.type
        if isinstance(t_self, BuiltinScalar):
            return t_self

    @cached_property
    def is_custom_scalar(self) -> Optional[Type[BaseCustomScalar]]:
        t_self = self.optional_maybe.type
        if t_self in self.scalars.values():
            return t_self

    @cached_property
    def annotation(self) -> str:
        """
        :returns: Annotation of the field based on the real type,
        meaning that the private attribute would be of that type.
        this goes for init and the property setter. They are optional by default,
        (at the template) so unwrap optional first
        """
        t_self = self.optional_maybe

        # int, str, float etc...
        if builtin_scalar := t_self.is_builtin_scalar:
            return builtin_scalar.tp.__name__

        if scalar := t_self.is_custom_scalar:
            return f"SCALARS.{scalar.__name__}"
        if gql_enum := t_self.is_enum:
            return gql_enum.name
        if model_of := t_self.is_model:
            return f"{QGraphQListModel.__name__}[{model_of.annotation}]"
        if object_def := t_self.is_object_type or t_self.is_interface:
            return f"Optional[{object_def.name}]"
        if t_self.is_union:
            return "Union[" + ", ".join(th.annotation for th in t_self.of_type) + "]"
        if input_obj := t_self.is_input_object_type:
            return input_obj.name

        raise NotImplementedError  # pragma no cover

    def as_annotation(self, object_map=None):  # pragma: no cover
        raise NotImplementedError("not safe to call on this type")
