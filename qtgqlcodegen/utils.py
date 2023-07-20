from __future__ import annotations

from typing import TYPE_CHECKING, Any, Hashable, Literal, TypeVar

from attr import define

if TYPE_CHECKING:
    from pathlib import Path


@define
class FileSpec:
    path: Path
    content: str

    def dump(self) -> None:
        self.path.write_text(self.content, "UTF-8")


class AntiForwardRef:
    """i.e:

    Union["someString"] would return a ForwardRef, this class is a
    simple hack to just return a type contains the name. Also, this is a
    workaround for types that reference each-other, otherwise it would
    cause recursion error.
    """

    name: str
    type_map: dict

    @classmethod
    def resolve(cls) -> Any:
        return cls.type_map[cls.name]


def anti_forward_ref(name: str, type_map: dict) -> type[AntiForwardRef]:
    return type(name, (AntiForwardRef,), {"name": name, "type_map": type_map})


UNSET: Any = Literal["UNSET"]

T = TypeVar("T")


def require(v: T | None) -> T:  # pragma: no cover
    if not v:
        raise AttributeError(f"{v} returned no value")
    return v


def freeze(self, key, value):  # pragma: no cover
    raise PermissionError("setattr called on frozen type")


def _replace_tuple_item(
    original: tuple,
    at: int,
    replace: tuple,
):
    return original[0:at] + replace + original[at + 1 : len(original)]


T_Key = TypeVar("T_Key", bound=Hashable)
T_Value = TypeVar("T_Value")


class HashAbleDict(dict[T_Key, T_Value]):
    """Dict that hashes the keys.

    supports only flat dicts.
    """

    def __hash__(self):
        return hash(frozenset(self.keys()))
