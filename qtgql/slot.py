import itertools
from typing import Any

from PySide6 import QtCore as qtc

from qtgql.typingref import TypeHinter


def get_optional_args(annotations: list[TypeHinter]) -> list[TypeHinter]:
    return [arg.of_type[0] for arg in annotations if arg.is_optional()]


def get_concretes(annotations: list[TypeHinter]) -> list[TypeHinter]:
    ret = []
    for item in annotations:
        annotations.remove(item)
        if item.is_optional():
            continue
        ret.append(item)
    return ret + annotations


def get_combos(stripped_optionals: list[TypeHinter], concretes: list[TypeHinter]):
    required_annotations = tuple([th.type for th in concretes])
    combos = []
    for i in range(len(stripped_optionals) + 1):
        for subset in itertools.combinations([th.type for th in stripped_optionals], i):
            combos.append(subset + required_annotations)
    return combos


def slot(func):
    def wrapper(func) -> func:
        anots: dict = func.__annotations__
        return_ = anots.pop("return", None)
        if return_ is Any:
            return_ = "QVariant"
        args = [TypeHinter.from_annotations(th) for th in anots.values()]
        stripped_optionals = get_concretes(get_optional_args(args))
        concretes = get_concretes(args)

        if stripped_optionals:
            combos = get_combos(stripped_optionals, concretes)
            for combo in combos:
                func = qtc.Slot(*combo, result=return_)(func)
            return func

        return qtc.Slot(*[th.type for th in concretes], result=return_)(func)

    return wrapper(func)
