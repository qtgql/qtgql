import enum
from functools import cached_property
from typing import List, Optional, Type, Union

from attrs import define

from qtgql.codegen.py.bases import _BaseQGraphQLObject
from qtgql.codegen.py.custom_scalars import CustomScalarMap
from qtgql.codegen.py.scalars import BaseCustomScalar, BuiltinScalars
from qtgql.codegen.utils import AntiForwardRef
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
            # might be a model, which has no type representation ATM.
            name = self.fget_annotation.replace("Model", "")
            assert self.type_map.get(name, None), f"{self.fget_annotation} Could not be resolved"
            # This is a QGraphQLObject, avoid undefined names.
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
    def is_scalar(self) -> bool:
        return (
            self.type.type in BuiltinScalars.values()
            or self.type.of_type in BuiltinScalars.values()
            and not self.is_custom_scalar
        )

    @cached_property
    def is_custom_scalar(self) -> Optional[Type[BaseCustomScalar]]:
        if self.type.type in self.scalars.values():
            return self.type.type
        return None

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
