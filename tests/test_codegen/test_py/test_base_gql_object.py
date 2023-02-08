from qtgql.codegen.py.bases import get_base_graphql_object


def test_default_is_singleton():
    class T(get_base_graphql_object("BO")):
        ...

    assert T.default_instance() is T.default_instance()
