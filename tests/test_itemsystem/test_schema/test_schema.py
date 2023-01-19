from __future__ import annotations

from qtgql.itemsystem import role
from qtgql.itemsystem.model import GenericModel
from qtgql.itemsystem.schema import Schema

pytest_plugins = ("tests.test_itemsystem.fixtures",)


def test_simple_schema(base_type):
    class Query(base_type):
        a: str = role()

    schema = Schema(query=Query)
    assert schema.types["Query"] is Query


def test_nested_types(base_type):
    class A(base_type):
        a: int = role()

    class B(base_type):
        b: str = role()

    class Query(base_type):
        a: GenericModel[A] = role()
        b: GenericModel[B] = role()

    schema = Schema(query=Query)
    assert schema.types[Query.__name__] is Query
    assert Query.Model.__roles__.children["a"] is A
    assert Query.Model.__roles__.children["b"] is B
    assert schema.types[B.__name__] is B
    assert schema.types[A.__name__] is A


def test_deferred_types(base_type):
    class Query(base_type):
        a: GenericModel[A] = role()
        b: GenericModel[B] = role()

    class A(base_type):
        a: int = role()

    class B(base_type):
        b: str = role()

    schema = Schema(query=Query)
    assert schema.types[Query.__name__] is Query
    assert Query.Model.__roles__.children["a"] is A
    assert Query.Model.__roles__.children["b"] is B
    assert schema.types[B.__name__] is B
    assert schema.types[A.__name__] is A


def test_get_node(model_with_child):
    node = model_with_child._data[0].child._data[0]
    result = model_with_child.schema.get_node(node)
    assert result.node == node
