import json
import re
from typing import Any, Generic, Optional, Type, TypeVar, Union
import uuid

from attr import asdict, define


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


@define
class EncodeAble:
    def asdict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not UNSET}


T = TypeVar("T")


@define(kw_only=True)
class QueryPayload(Generic[T], EncodeAble):
    query: str
    operationName: Optional[str] = UNSET
    variables: Optional[Union[dict, T]] = UNSET

    def __attrs_post_init__(self):
        match = re.search(r"(subscription|mutation|query)(.*?({|\())", self.query)
        op_name = match.group(2).replace(" ", "").strip("{").strip("(")
        if op_name:
            self.operationName = op_name


@define(kw_only=True, repr=False)
class SafeGqlPayload(QueryPayload):
    ...


@define(kw_only=True)
class GqlResult:
    data: dict
    errors: Optional[list[dict]] = None


class GqlEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):  # noqa: R505
            return str(obj)
        elif isinstance(obj, (EncodeAble, QueryPayload)):
            return obj.asdict()
        return None
