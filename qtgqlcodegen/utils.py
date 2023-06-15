from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, TypeVar

from attr import define

if TYPE_CHECKING:
    from pathlib import Path


@define
class FileSpec:
    path: Path
    content: str

    def dump(self) -> None:
        self.path.write_text(self.content)


class AntiForwardRef:
    """
    i.e:
    Union["someString"] would return a ForwardRef, this class is a simple hack
    to just return a type contains the name.
    Also, this is a workaround for types that reference each-other,
    otherwise it would cause recursion error.
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
