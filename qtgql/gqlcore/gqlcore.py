import json
import re
import uuid
from typing import Generic, Optional, TypeVar, Union

from attr import asdict, define

from qtgql.typingref import UNSET


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
