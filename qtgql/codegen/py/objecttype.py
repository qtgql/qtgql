import enum
from functools import cached_property
from typing import TYPE_CHECKING, Any, List, Optional, Union

from attrs import define

from qtgql.codegen.py.bases import _BaseQGraphQLObject
from qtgql.codegen.py.scalars import BuiltinScalars, CustomScalarMap
from qtgql.codegen.utils import AntiForwardRef
from qtgql.typingref import TypeHinter

if TYPE_CHECKING:
    from qtgql.codegen.py.scalars import BaseCustomScalar


class Kinds(enum.Enum):
    SCALAR = "SCALAR"
    OBJECT = "OBJECT"
    ENUM = "ENUM"
    LIST = "LIST"
    UNION = "UNION"
    NON_NULL = "NON_NULL"

    def __getitem__(self, item):
        for f in Kinds:
            if f.name == item:
                return item
        raise KeyError(item, "is a wrong kind")


def stringify_annotation(annot: Any) -> str:
    return str(annot).replace("typing.", "").replace("qtgql.codegen.utils.", "")


@define(slots=False)
class FieldProperty:
    name: str
    type: TypeHinter
    type_map: dict[str, "GqlType"]
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
        if t in self.scalars.values():
            t: BaseCustomScalar
            return f"SCALARS.{t.__name__}.{BaseCustomScalar.from_graphql.__name__}({default})"
        if t in (list, List):
            inner = type_hinter.of_type[0].type
            # handle inner type
            assert issubclass(inner, AntiForwardRef)
            gql_type = self.type_map[inner.name]
            return f"cls.{_BaseQGraphQLObject.deserialize_list_of.__name__}(parent, data, {gql_type.model_name}, '{self.name}', {gql_type.name})"
        if t is Union:
            return (
                f"cls.{_BaseQGraphQLObject.deserialize_union.__name__}(parent, data, '{self.name}')"
            )
        # handle inner type
        assert issubclass(t, AntiForwardRef)
        if t.name in self.type_map.keys():
            return f"cls.{_BaseQGraphQLObject.deserialize_optional_child.__name__}(parent, data, {t.name}, '{self.name}')"
        raise NotImplementedError

    @cached_property
    def annotation(self) -> str:
        """
        :returns: Annotation of the field based on the type.
        """
        ret = self.type.as_annotation()
        # int, str, float etc...
        if ret in BuiltinScalars.values():
            return ret.__name__

        if ret in self.scalars.values():
            ret: BaseCustomScalar
            return f"SCALARS.{ret.__name__}"

        # handle Optional, Union, List etc...
        # removing redundant prefixes.
        return stringify_annotation(ret)

    @cached_property
    def property_type(self) -> str:
        if (
            self.type.type in BuiltinScalars.values()
            or self.type.of_type in BuiltinScalars.values()
        ):
            return self.annotation
        elif scalar := self.is_custom_scalar:
            return stringify_annotation(scalar.to_qt.__annotations__["return"])
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

    @cached_property
    def is_custom_scalar(self) -> Optional[BaseCustomScalar]:
        if self.type.type in self.scalars.values():
            return self.type.type

    @property
    def fget(self) -> str:
        if self.is_custom_scalar:
            return f"return self.{self.private_name}.{BaseCustomScalar.to_qt.__name__}()"
        return f"return self.{self.private_name}"


@define(slots=False)
class GqlType:
    kind: Kinds
    name: str
    fields: list["FieldProperty"]
    docstring: Optional[str] = ""

    @cached_property
    def model_name(self) -> str:
        return self.name + "Model"
