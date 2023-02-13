from tests.test_codegen.test_py.test_introspection_generator import ScalarsTestCase


def test_simple_query_generation(qmlbot, mini_server):
    testcase = ScalarsTestCase.compile(mini_server.address)
    testcase.load_qml(qmlbot)
    testcase.get_environment()
