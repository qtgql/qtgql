import pytest
from qtgql.codegen.py.runtime.environment import ENV_MAP, QtGqlEnvironment
from qtgql.gqltransport.client import GqlWsTransportClient


@pytest.fixture()
def pseudo_environment():
    ENV_MAP["DEFAULT"] = QtGqlEnvironment(GqlWsTransportClient(url=""))
    yield ENV_MAP["DEFAULT"]
    ENV_MAP.pop("DEFAULT")
