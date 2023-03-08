import itertools
from typing import Any, Callable, TypeVar, get_type_hints

from PySide6 import QtCore

from qtgql.utils.typingref import TypeHinter


def get_combos(stripped_optionals: list[TypeHinter], concretes: list[TypeHinter]):
    required_annotations = tuple([th.type for th in concretes])
    combos = []
    for i in range(len(stripped_optionals) + 1):
        for subset in itertools.combinations([th.type for th in stripped_optionals], i):
            combos.append(subset + required_annotations)
    return combos


T_Callable = TypeVar("T_Callable", bound=Callable)


def slot(func: T_Callable) -> T_Callable:
    def wrapper(func) -> T_Callable:
        anots: dict = get_type_hints(func)
        return_ = TypeHinter.from_annotations(anots.pop("return", None))
        if return_.type is type(None):
            ret_type = None
        elif return_.type is Any:
            ret_type = "QVariant"
        else:
            ret_type = return_.type

        args = [TypeHinter.from_annotations(th) for th in anots.values()]

        stripped_optionals = [th.of_type[0] for th in args if th.is_optional()]
        concretes = [th for th in args if not th.is_optional()]

        if stripped_optionals:
            combos = get_combos(stripped_optionals, concretes)
            for combo in combos:
                func = QtCore.Slot(*combo, result=ret_type)(func)
            return func
        return QtCore.Slot(*[th.type for th in concretes], result=ret_type)(func)

    return wrapper(func)
