import re
from typing import NamedTuple

from qtgql.codegen.py.objecttype import GqlFieldDefinition

pattern = re.compile(r"(?s)(?<=graphql: `).*?(?=`)")


def find_gql(string: str) -> list[str]:
    return pattern.findall(string)


class QueryHandlerDefinition(NamedTuple):
    query: str
    name: str
    field: GqlFieldDefinition
    directives: list[str] = []
    fragments: list[str] = []
