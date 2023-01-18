import attrs

from tests.test_itemsystem.fixtures import NORMAL_GQL_CAMELIZED, FullClass

pytest_plugins = ("tests.test_itemsystem.fixtures",)


def test_update_node(model_with_child):
    before: FullClass = model_with_child._data[0].child._data[0]
    TEST_NODE_UPDATE = "TEST_NODE_UPDATE"
    assert before.normalGql != TEST_NODE_UPDATE
    new_node = attrs.evolve(before, **{NORMAL_GQL_CAMELIZED: TEST_NODE_UPDATE})
    new_node.normalGql = TEST_NODE_UPDATE
    assert before != new_node
    assert before.uuid == new_node.uuid
    model_with_child.schema.update_node(new_node)
    after_update = model_with_child._data[0].child._data[0]
    assert after_update == new_node
