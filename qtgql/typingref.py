from typing import Any, NamedTuple, Optional, Type, Union, get_args, get_origin


def is_optional(field) -> bool:
    return get_origin(field) is Union and type(None) in get_args(field)


class UnsetType:
    __instance: Optional["UnsetType"] = None

    def __new__(cls: Type["UnsetType"]) -> "UnsetType":
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            return cls.__instance
        return cls.__instance

    def __str__(self):
        return ""

    def __repr__(self) -> str:  # pragma: no cover
        return "UNSET"

    def __bool__(self):
        return False


UNSET: Any = UnsetType()


class TypeHinter(NamedTuple):
    type: Any  # noqa: A003
    of_type: Optional[tuple["TypeHinter"]]

    @classmethod
    def from_annotations(cls, tp: Any) -> "TypeHinter":
        if args := get_args(tp):
            new_args: list[TypeHinter] = []
            for arg in args:
                new_args.append(TypeHinter.from_annotations(arg))
            return TypeHinter(type=get_origin(tp), of_type=tuple(new_args))  # type: ignore
        return TypeHinter(type=tp, of_type=None)
