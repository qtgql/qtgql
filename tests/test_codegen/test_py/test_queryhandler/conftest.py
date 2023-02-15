import pytest
from qtgql.codegen.py.runtime.environment import _ENV_MAP, QtGqlEnvironment, set_gql_env
from qtgql.gqltransport.client import GqlWsTransportClient


@pytest.fixture()
def pseudo_environment():
    env = QtGqlEnvironment(GqlWsTransportClient(url=""), name="PSEUDO")
    set_gql_env(env)
    yield env
    _ENV_MAP.pop(env.name)
