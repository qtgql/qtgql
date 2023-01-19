import itertools
from typing import Any, Optional, get_args

from PySide6 import QtCore as qtc

from qtgql.typingref import is_optional


def get_optional_args(annotations: list[Any]) -> list[Any]:
    return [get_args(arg)[0] for arg in annotations if is_optional(arg)]


def get_concrete(annotation: Any) -> Optional[type]:
    return getattr(annotation, "__origin__", None)


def get_concretes(annotations: list) -> list:
    ret = []
    for item in annotations:
        if is_optional(item):
            annotations.remove(item)
            continue
        if concrete := get_concrete(item):
            ret.append(concrete)
            annotations.remove(item)
    return ret + annotations


def slot(func):
    def wrapper(func) -> func:
        anots: dict = func.__annotations__
        return_ = anots.pop("return", None)
        if return_ is Any:
            return_ = "QVariant"
        args = list(anots.values())
        stripped_optionals = get_concretes(get_optional_args(args))
        concretes = get_concretes(args)

        if stripped_optionals:
            required_annotations = tuple(concretes)
            combos = []
            for i in range(len(stripped_optionals) + 1):
                for subset in itertools.combinations(stripped_optionals, i):
                    combos.append(subset)
            for combo in combos:
                func = qtc.Slot(*combo + required_annotations, result=return_)(func)

            return func

        return qtc.Slot(*concretes, result=return_)(func)

    return wrapper(func)
