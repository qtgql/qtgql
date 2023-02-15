from unittest.mock import MagicMock

from qtgql.codegen.py.runtime.queryhandler import BaseQueryHandler


def test_is_singleton(pseudo_environment):
    class Foo(BaseQueryHandler):
        ...

    assert Foo() is Foo()

    class Bar(BaseQueryHandler):
        ...

    assert Bar() is not Foo()


def test_fetch_when_graphql_is_set(pseudo_environment):
    class Foo(BaseQueryHandler):
        ...

    inst = Foo()
    inst.fetch = MagicMock()
    Foo().set_graphql("bar")
    assert inst.fetch.called
