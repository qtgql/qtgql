from __future__ import annotations

import contextlib
import enum
from functools import cached_property
from typing import List, Optional, Type, Union

from attrs import define

from qtgql.codegen.py.bases import _BaseQGraphQLObject
from qtgql.codegen.py.custom_scalars import CustomScalarMap
from qtgql.codegen.py.scalars import BaseCustomScalar, BuiltinScalars
from qtgql.codegen.utils import AntiForwardRef
from qtgql.typingref import TypeHinter, ensure


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
class FieldProperty:
    name: str
    type: TypeHinter
    type_map: dict[str, GqlTypeDefinition]
    enums: "EnumMap"
    scalars: CustomScalarMap
    description: Optional[str] = ""

    @cached_property
    def deserializer(self) -> str:
        """If the field is optional this would be."""
        # every thing is possibly optional since you can query for only so or so fields.
        default = f"data.get('{self.name}', None)"
        t = self.type.type
        type_hinter = self.type
        if t is Optional:
            t = self.type.of_type[0].type
            type_hinter = self.type.of_type[0]

        if t in BuiltinScalars.values():
            return default

        if scalar := self.is_custom_scalar:
            return f"SCALARS.{scalar.__name__}.{BaseCustomScalar.from_graphql.__name__}({default})"
        if t in (list, List):
            inner = type_hinter.of_type[0].type
            # handle inner type
            assert issubclass(inner, AntiForwardRef)
            # enums are not supported in lists yet (valid graphql spec though)
            gql_type = ensure(inner.resolve(), GqlTypeDefinition)
            assert gql_type
            return f"cls.{_BaseQGraphQLObject.deserialize_list_of.__name__}(parent, data, {gql_type.model_name}, '{self.name}', {gql_type.name})"
        if t is Union:
            return (
                f"cls.{_BaseQGraphQLObject.deserialize_union.__name__}(parent, data, '{self.name}')"
            )
        # handle inner type if it was optional above
        assert issubclass(t, AntiForwardRef)
        # graphql object
        if gql_type := self.is_object_type:
            return f"cls.{_BaseQGraphQLObject.deserialize_optional_child.__name__}(parent, data, {gql_type.name}, '{self.name}')"
        elif isinstance(t.resolve(), GqlEnumDefinition):
            return f"{t.name}[data.get('{self.name}', 1)]"  # graphql enums evaluates to string of the name.
        raise NotImplementedError  # pragma: no cover

    @cached_property
    def annotation(self) -> str:
        """
        :returns: Annotation of the field based on the real type,
        meaning that the private attribute would be of that type.
        this goes for init and the property setter.
        """
        ret = self.type.as_annotation()
        # int, str, float etc...
        if ret in BuiltinScalars.values():
            return ret.__name__

        if scalar := self.is_custom_scalar:
            return f"SCALARS.{scalar.__name__}"
        if gql_enum := self.is_enum:
            return gql_enum.name
        # handle Optional, Union, List etc...
        # removing redundant prefixes.
        return TypeHinter.from_annotations(ret).stringify()

    @cached_property
    def fget_annotation(self) -> str:
        """This annotates the value that is QML-compatible."""
        ret = self.type
        if ret.is_optional():
            ret = self.type.of_type[0]

        if ret.type in BuiltinScalars.values():
            return self.annotation
        if scalar := self.is_custom_scalar:
            return TypeHinter.from_annotations(scalar.to_qt.__annotations__["return"]).stringify()
        if ret.is_list():
            return self.type_map[ret.of_type[0].type.name].model_name
        if self.is_enum:
            return "int"

        return ret.stringify()

    @cached_property
    def property_type(self) -> str:
        try:
            # this should raise if it is an inner type.
            ret = TypeHinter.from_string(self.fget_annotation, self.type_map)
            if ret.is_optional():
                return ret.of_type[0].stringify()
            if ret.type in self.type_map.values():
                raise TypeError  # in py3.11 the get_type_hints won't raise so raise brutally
            return self.fget_annotation
        except (TypeError, NameError):
            if self.type.is_union():
                return "QObject"  # graphql doesn't support scalars in Unions ATM.
            if self.is_enum:
                # QEnum value must be int
                return "int"
            # might be a model, which is also QObject
            assert self.is_model or self.is_object_type
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

    @staticmethod
    def unwrap_optional(th: TypeHinter) -> TypeHinter:
        if th.is_optional():
            return th.of_type[0]
        return th

    @cached_property
    def is_object_type(self) -> Optional[GqlTypeDefinition]:
        t = self.type.type
        if self.type.is_optional():
            t = self.type.of_type[0].type
        with contextlib.suppress(TypeError):
            if issubclass(t, AntiForwardRef):
                ret = t.resolve()
                if isinstance(ret, GqlTypeDefinition):
                    return ret

    @cached_property
    def is_model(self) -> Optional[GqlTypeDefinition]:
        th = self.type
        if th.is_optional():
            th = th.of_type[0]
        if th.is_list():
            th = th.of_type[0]
        with contextlib.suppress(TypeError):
            if issubclass(th.type, AntiForwardRef):
                ret = th.type.resolve()
                if isinstance(ret, GqlTypeDefinition):
                    return ret

    @cached_property
    def is_scalar(self) -> bool:
        return (
            self.type.type in BuiltinScalars.values()
            or self.type.of_type in BuiltinScalars.values()
            and not self.is_custom_scalar
        )

    @cached_property
    def is_enum(self) -> Optional["GqlEnumDefinition"]:
        tp = self.unwrap_optional(self.type)
        with contextlib.suppress(TypeError):
            if issubclass(tp.type, AntiForwardRef):
                if isinstance(tp.type.resolve(), GqlEnumDefinition):
                    return tp.type.resolve()

    @cached_property
    def is_custom_scalar(self) -> Optional[Type[BaseCustomScalar]]:
        tp = self.unwrap_optional(self.type)
        if tp.type in self.scalars.values():
            return tp.type

    @property
    def fget(self) -> str:
        if self.is_custom_scalar:
            return f"return self.{self.private_name}.{BaseCustomScalar.to_qt.__name__}()"
        if self.is_enum:
            return f"return self.{self.private_name}.value"
        return f"return self.{self.private_name}"


@define(slots=False)
class GqlTypeDefinition:
    kind: Kinds
    name: str
    fields: list[FieldProperty]
    docstring: Optional[str] = ""

    @cached_property
    def model_name(self) -> str:
        return "Q" + self.name + "Model"


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
