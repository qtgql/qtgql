import pytest

from tests.mini_gql_server import schema


@pytest.fixture
def introspection_query() -> dict:
    return schema
