from tests.test_codegen.test_py.test_introspection_generator import ScalarsTestCase


def test_simple_query_generation():
    comp = """
    import QtQuick
    UseQuery{
        property var query: graphql`query MainAppQuery {
        user{
        name
        age
        }
        }`
    }
    """
    testcase = ScalarsTestCase.compile()
    testcase.evaluator._evaluate_query(comp)
