from qtgql.itemsystem import role


def test_builtin(base_type):
    class Foo(base_type):
        bar: str = role()

    Foo.Model(data=[{"bar": "baz"}])
