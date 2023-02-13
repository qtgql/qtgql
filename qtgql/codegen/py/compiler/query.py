import re
from typing import NamedTuple

from qtgql.codegen.py.objecttype import GqlFieldDefinition
from qtgql.gqltransport.client import HandlerProto


class UseQueryHandler(HandlerProto):
    ...


pattern = re.compile(r"(?s)(?<=graphql`).*?(?=`)")


def find_gql(string: str) -> list:
    return pattern.findall(string)


def hash_query(query: str) -> int:
    return hash(query)


class GqlQueryDefinition(NamedTuple):
    query: str
    name: str
    field: GqlFieldDefinition
    directives: list[str] = []
    fragments: list[str] = []
