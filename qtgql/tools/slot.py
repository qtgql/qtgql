import itertools
from typing import Any

from PySide6 import QtCore

from qtgql.utils.typingref import TypeHinter


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
        stripped_optionals = [th.of_type[0] for th in args if th.is_optional()]
        concretes = [th for th in args if not th.is_optional()]

        if stripped_optionals:
            combos = get_combos(stripped_optionals, concretes)
            for combo in combos:
                func = QtCore.Slot(*combo, result=return_)(func)
            return func

        return QtCore.Slot(*[th.type for th in concretes], result=return_)(func)

    return wrapper(func)
