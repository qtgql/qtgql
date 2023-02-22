import types
from typing import Any, Type, TypeVar, Union, cast, get_args

import attr
from attr import Attribute, define
from PySide6 import QtCore
from typing_extensions import dataclass_transform

__all__ = ["define_properties"]


def signal_name(name: str) -> str:
    return name + "Changed"


class PropertyMeta(type(QtCore.QObject)):  # type: ignore
    def __new__(cls, name, bases, attrs):
        return super().__new__(cls, name, bases, attrs)


class BaseInner(QtCore.QObject):
    def __init__(self, attrs_instance, parent=None):
        super().__init__(parent)
        self.attrs_instance = attrs_instance


class PropertyImpl(QtCore.Property):
    def __init__(self, type_: type, name: str, notify: QtCore.Signal):
        self.name = name
        super().__init__(type_, fget=self.getter, fset=self.setter, notify=notify)  # type: ignore

    def getter(self, instance: BaseInner):  # type: ignore
        return getattr(instance.attrs_instance, f"{self.name}")

    def setter(self, instance: BaseInner, value):  # type: ignore
        signal = getattr(instance, signal_name(self.name))
        setattr(instance.attrs_instance, f"{self.name}", value)
        signal.emit()


class MakeProperties:
    PropertiesClass_: Type[BaseInner]
    properties: BaseInner

    def __init_subclass__(cls, **kwargs) -> None:
        annotations: dict[str, type] = cls.__annotations__
        properties: dict[str, Union[PropertyImpl, QtCore.Signal]] = {}
        signals: dict[str, QtCore.Signal] = {}
        for key in cls.__dict__:
            if key in annotations:
                type_ = annotations[key]
                if args := get_args(type_):
                    type_ = args[0]
                if type_ is Any:
                    type_ = "QVariant"  # type: ignore
                signals[signal_name(key)] = signal = QtCore.Signal()
                properties[key] = PropertyImpl(type_=type_, name=key, notify=signal)

        inner = types.new_class(
            name=cls.__name__ + "Properties",
            bases=(BaseInner,),
            kwds={"metaclass": PropertyMeta},
            exec_body=lambda ns: ns.update(dict(**signals, **properties)),
        )
        cls.PropertiesClass_ = inner


def attrs_compat_setter(instance: "BasePropertyClass", attr: Attribute, value):
    getattr(instance.properties, signal_name(attr.name)).emit()
    return value


T = TypeVar("T")

BasePropertyClass = TypeVar("BasePropertyClass", bound=MakeProperties)


@dataclass_transform(
    field_descriptors=(attr.attrib, attr.field),
)
def define_properties(cls: Union[Type[T], Type[MakeProperties]]) -> Type[BasePropertyClass]:
    """
    :param cls: Class that implements dataclass syntax - (PEP 681).
    :return: `@attrs.define` decorated class with properties field injected.
     this field is a `QObject` that will emit signals when you set attribute on that class
     and is use-able via QML and other parts of QT.
    """
    ns = cls.__dict__.copy()
    bases = cls.__bases__ if cls.__bases__ != (object,) else (MakeProperties,)
    cls = type(cls.__name__, bases, ns)

    def post_init(self: BasePropertyClass):
        self.properties = self.PropertiesClass_(self)

    cls.__attrs_post_init__ = post_init  # type: ignore
    return cast(Type[BasePropertyClass], define(cls, on_setattr=attrs_compat_setter))
