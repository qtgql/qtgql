import json
import uuid
from typing import Generic
from typing import Optional
from typing import TypeVar
from typing import Union

from attr import asdict
from attr import define
from typingref import UNSET

from qtgql.utils.graphql import get_operation_name


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
        if not self.operationName:
            self.operationName = get_operation_name(self.query)


@define(kw_only=True, repr=False)
class SafeGqlPayload(QueryPayload):
    ...


@define(kw_only=True)
class GqlResult:
    data: dict
    errors: Optional[list[dict]] = None


class GqlEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, (EncodeAble, QueryPayload)):
            return obj.asdict()
