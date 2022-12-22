from qtgql.itemsystem import BaseRoleDefined, role
from qtgql.itemsystem.schema import Schema

pytest_plugins = ("tests.test_itemsystem.fixtures",)


def test_simple_schema():
    class Query(BaseRoleDefined):
        a: str = role()

    schema = Schema(query=Query)
    assert schema.types["Query"] is Query


def test_nested_types():
    class A(BaseRoleDefined):
        a: int = role()

    class B(BaseRoleDefined):
        b: str = role()

    class Query(BaseRoleDefined):
        a: list[A] = role()
        b: list[B] = role()

    schema = Schema(query=Query)
    assert schema.types[Query.__name__] is Query
    assert schema.types[B.__name__] is B
    assert schema.types[A.__name__] is A


def test_deferred_types():
    class Query(BaseRoleDefined):
        a: list["A"] = role()
        b: list["B"] = role()

    class A(BaseRoleDefined):
        a: int = role()

    class B(BaseRoleDefined):
        b: str = role()

    schema = Schema(query=Query)
    assert schema.types[Query.__name__] is Query
    assert schema.types[B.__name__] is B
    assert schema.types[A.__name__] is A


def test_get_node(model_with_child):
    raise NotImplementedError
    # node: FullClass = model_with_child._data[0].child._data[0]
    # result = model_with_child.get_node(node)
    # assert result.node == node
