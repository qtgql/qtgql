from typing import Type


class AntiForwardRef:
    """
    i.e:
    Union["someString"] would return a ForwardRef, this class is a simple hack
    to just return a type contains the name.
    """

    name: str


def anti_forward_ref(name: str) -> Type[AntiForwardRef]:
    return type(name, (AntiForwardRef,), {"name": name})
