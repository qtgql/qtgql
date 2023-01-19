from typing import List

import graphql

from qtgql.compiler.objecttype import GqlType

query = graphql.get_introspection_query(descriptions=True)


def introspect(url: str) -> List[GqlType]:
    raise NotImplementedError
