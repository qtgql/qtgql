from __future__ import annotations

from qtgql.itemsystem import role
from qtgql.itemsystem.schema import Schema

pytest_plugins = ("tests.test_itemsystem.fixtures",)


def test_simple_schema(types_storage):
    @types_storage.register
    class Query:
        a: str = role()

    schema = Schema(query=Query, types_storage=types_storage)
    assert schema.types["Query"] is Query


def test_nested_types(types_storage):
    @types_storage.register
    class A:
        a: int = role()

    @types_storage.register
    class B:
        b: str = role()

    @types_storage.register
    class Query:
        a: list[A] = role()
        b: list[B] = role()

    schema = Schema(query=Query, types_storage=types_storage)
    assert schema.types[Query.__name__] is Query
    assert Query.__roles__.children["a"] is A
    assert Query.__roles__.children["b"] is B
    assert schema.types[B.__name__] is B
    assert schema.types[A.__name__] is A


def test_deferred_types(types_storage):
    @types_storage.register
    class Query:
        a: list[A] = role()
        b: list[B] = role()

    @types_storage.register
    class A:
        a: int = role()

    @types_storage.register
    class B:
        b: str = role()

    schema = Schema(query=Query, types_storage=types_storage)
    assert schema.types[Query.__name__] is Query
    assert Query.__roles__.children["a"] is A
    assert Query.__roles__.children["b"] is B
    assert schema.types[B.__name__] is B
    assert schema.types[A.__name__] is A


def test_get_node(model_with_child):
    raise NotImplementedError
    # node: FullClass = model_with_child._data[0].child._data[0]
    # result = model_with_child.get_node(node)
    # assert result.node == node
