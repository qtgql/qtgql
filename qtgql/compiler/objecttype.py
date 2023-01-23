import enum
from functools import cached_property
from typing import Optional

from attrs import define

from qtgql.compiler.utils import AntiForwardRef
from qtgql.typingref import TypeHinter


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


@define(slots=False)
class FieldProperty:
    name: str
    type: TypeHinter
    type_map: dict[str, "GqlType"]
    description: Optional[str] = ""

    @cached_property
    def deserializer(self) -> str:
        """If the field is optional this would be."""

        default = f"data['{self.name}']"
        t = self.type.type
        if t is Optional:
            inner = self.type.of_type[0].type
            if inner in BuiltinScalars.values():
                return f"data.get('{self.name}', None)"
            # handle inner type
            assert issubclass(inner, AntiForwardRef)
            if inner.name in self.type_map.keys():
                return f"deserialize_optional_child(data, {inner.name}, '{self.name}')"

        if t in BuiltinScalars.values():
            return default
        # handle inner type
        assert issubclass(t, AntiForwardRef)
        if t.name in self.type_map.keys():
            return f"{t.name}.from_dict({default})"
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
        # handle Optional, Union, List etc...
        # removing redundant prefixes.
        return str(ret).replace("typing.", "").replace("qtgql.compiler.utils.", "")

    @cached_property
    def property_type(self) -> str:
        if (
            self.type.type in BuiltinScalars.values()
            or self.type.of_type in BuiltinScalars.values()
        ):
            return self.annotation
        return '"QVariant"'

    @cached_property
    def setter_name(self) -> str:
        return self.name + "_setter"

    @cached_property
    def signal_name(self) -> str:
        return self.name + "Changed"

    @cached_property
    def private_name(self) -> str:
        return "_" + self.name


@define
class GqlType:
    kind: Kinds
    name: str
    fields: list["FieldProperty"]
    docstring: Optional[str] = ""


BuiltinScalars: dict[str, type] = {
    "Int": int,
    "Float": float,
    "String": str,
    "ID": str,
    "Boolean": bool,
}
