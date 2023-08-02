from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any, Callable, Hashable, Literal, TypeVar

from attr import define

if TYPE_CHECKING:
    from pathlib import Path


@define
class FileSpec:
    path: Path
    content: str

    def dump(self) -> None:
        self.path.write_text(self.content, "UTF-8")


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


def cached_method():
    def wrapper(fn: Callable):
        cache_name = f"{fn.__name__}__cache"

        @functools.wraps(fn)
        def cacher(self, *args, **kwargs):
            if kwargs:  # pragma: no cover
                raise Exception(f"cached method must be used with kwargs. got {kwargs}")
            cache: dict = getattr(self, cache_name, None)
            if not cache:
                cache = {}
                setattr(self, cache_name, cache)

            hashed = hash(args)
            ret = cache.get(hashed, None)
            if not ret:
                ret = fn(self, *args)
                cache[hashed] = ret
            return ret

        return cacher

    return wrapper
