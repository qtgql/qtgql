from types import ModuleType
from typing import Any, Callable

import pytest
from qtgql.compiler.py.compiler import GqlType, PropertyImpl, SchemaTemplate


@pytest.fixture
def default_types() -> list[GqlType]:
    return [
        GqlType(
            docstring="Hello", name="MyType", properties=[PropertyImpl(name="someProp", type=int)]
        ),
        GqlType(
            docstring="Hello",
            name="MyType2",
            properties=[PropertyImpl(name="someProp2", type=float)],
        ),
    ]


@pytest.fixture()
def tmp_mod():
    return ModuleType("testmodule")


def test_simple_compile(default_types, tmp_mod):
    res = SchemaTemplate.render(types=default_types)
    compiled = compile(res, "<string>", "exec")
    exec(compiled, tmp_mod.__dict__)


@pytest.fixture()
def compiled(default_types, tmp_mod):
    res = SchemaTemplate.render(types=default_types)
    compiled = compile(res, "schema", "exec")
    exec(compiled, tmp_mod.__dict__)
    return tmp_mod


def test_has_class_name(default_types, compiled):
    for t in default_types:
        assert hasattr(compiled, t.name)


def property_tester(
    default_types: list[GqlType], compiled_mod, test: Callable[[PropertyImpl, Any], None]
):
    for t in default_types:
        cls = getattr(compiled_mod, t.name)
        for prop in t.properties:
            test(prop, cls)


def test_has_properties(default_types, compiled):
    def do(prop: PropertyImpl, cls):
        assert hasattr(cls, prop.name)

    property_tester(default_types, compiled, do)


def test_has_setter(default_types, compiled):
    def do(prop: PropertyImpl, cls):
        assert hasattr(cls, prop.setter_name)

    property_tester(default_types, compiled, do)


def test_has_signal(default_types, compiled):
    def do(prop: PropertyImpl, cls):
        assert hasattr(cls, prop.signal_name)

    property_tester(default_types, compiled, do)


def generate_type_kwargs(t: GqlType, v) -> dict:
    return {p.name: v for p in t.properties}


def test_init(default_types, compiled):
    for t in default_types:
        cls = getattr(compiled, t.name)
        inst = cls(**generate_type_kwargs(t, 1))
        for p in t.properties:
            assert getattr(inst, p.private_name) == 1


def test_property_getter(default_types, compiled):
    for t in default_types:
        cls = getattr(compiled, t.name)
        inst = cls(**generate_type_kwargs(t, 1))
        for p in t.properties:
            assert getattr(inst, p.name) == 1


def test_property_setter(default_types, compiled):
    for t in default_types:
        cls = getattr(compiled, t.name)
        inst = cls(**generate_type_kwargs(t, 1))
        for p in t.properties:
            getattr(inst, p.setter_name)(2)
            assert getattr(inst, p.name) == 2


def test_setter_emits_signal(qtbot, default_types, compiled):
    for t in default_types:
        cls = getattr(compiled, t.name)
        inst = cls(**generate_type_kwargs(t, 1))
        for p in t.properties:
            signal = getattr(inst, p.signal_name)
            with qtbot.wait_signal(signal):
                getattr(inst, p.setter_name)(2)
            assert getattr(inst, p.name) == 2
