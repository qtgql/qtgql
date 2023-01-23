import graphql
from strawberry.schema import Schema


def get_introspection_for(schema: Schema) -> dict:
    return schema.execute_sync(graphql.get_introspection_query()).data
