from tests.test_codegen.test_py.testcases import ScalarsTestCase


def test_get_node():
    testcase = ScalarsTestCase.compile()
    testcase.query_handler.on_data(testcase.initialize_dict)
    inst = testcase.query_handler.data
    store = testcase.gql_type.__store__
    assert store.get_node(inst.id) is inst


def test_loosing_node_deletes_it_from_store():
    testcase = ScalarsTestCase.compile()
    testcase.query_handler.on_data(testcase.initialize_dict)
    inst = testcase.query_handler.data
    store = testcase.gql_type.__store__
    store.loose(inst, testcase.query_handler.OPERATION_METADATA.operation_name)
    assert not store.get_node(inst.id)
