from qtgql.codegen.py.runtime.bases import get_base_graphql_object


def test_default_is_singleton():  # TODO: might be redundant at this point .
    class T(get_base_graphql_object("BO")):
        ...

    assert T.default_instance() is T.default_instance()
