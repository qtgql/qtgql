from typing import Type


class AntiRefMeta(type):
    def __str__(self):
        return self.__name__


class AntiForwardRef(metaclass=AntiRefMeta):
    """
    i.e:
    Union["someString"] would return a ForwardRef, this class is a simple hack
    to just return a type contains the name.
    """

    name: str


def anti_forward_ref(name: str) -> Type[AntiForwardRef]:
    return type(name, (AntiForwardRef,), {"name": name})
