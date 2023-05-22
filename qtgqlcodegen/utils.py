import re
from pathlib import Path
from typing import Any
from typing import Optional
from typing import Type

from attr import define


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


def anti_forward_ref(name: str, type_map: dict) -> Type[AntiForwardRef]:
    return type(name, (AntiForwardRef,), {"name": name, "type_map": type_map})


def get_operation_name(query: str) -> Optional[str]:
    if match := re.search(r"(subscription|mutation|query)(.*?({|\())", query):
        return match.group(2).replace(" ", "").strip("{").strip("(")
