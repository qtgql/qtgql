import pytest
from qtgql.compiler.objecttype import FieldProperty, GqlType, Kinds
from qtgql.compiler.py.compiler import SchemaTemplate
from qtgql.typingref import TypeHinter

from tests.test_compiler.test_py.conftest import generate_type_kwargs, property_tester


@pytest.fixture
def default_types() -> list[GqlType]:
    return [
        GqlType(
            docstring="Hello",
            kind=Kinds.OBJECT,
            name="MyType",
            fields=[FieldProperty(name="someProp", type_map={}, type=TypeHinter(type=int))],
        ),
        GqlType(
            docstring="Hello",
            kind=Kinds.OBJECT,
            name="MyType2",
            fields=[FieldProperty(name="someProp2", type_map={}, type=TypeHinter(type=str))],
        ),
    ]


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


def test_has_properties(default_types, compiled):
    def do(prop: FieldProperty, cls):
        assert hasattr(cls, prop.name)

    property_tester(default_types, compiled, do)


def test_has_setter(default_types, compiled):
    def do(prop: FieldProperty, cls):
        assert hasattr(cls, prop.setter_name)

    property_tester(default_types, compiled, do)


def test_has_signal(default_types, compiled):
    def do(prop: FieldProperty, cls):
        assert hasattr(cls, prop.signal_name)

    property_tester(default_types, compiled, do)


def test_init(default_types, compiled):
    for t in default_types:
        cls = getattr(compiled, t.name)
        inst = cls(**generate_type_kwargs(t, 1))
        for p in t.fields:
            assert getattr(inst, p.private_name) == 1


def test_property_getter(default_types, compiled):
    for t in default_types:
        cls = getattr(compiled, t.name)
        inst = cls(**generate_type_kwargs(t, 1))
        for p in t.fields:
            assert getattr(inst, p.name) == 1


def test_property_setter(default_types, compiled):
    for t in default_types:
        cls = getattr(compiled, t.name)
        inst = cls(**generate_type_kwargs(t, 1))
        for p in t.fields:
            getattr(inst, p.setter_name)(2)
            assert getattr(inst, p.name) == 2


def test_setter_emits_signal(qtbot, default_types, compiled):
    for t in default_types:
        cls = getattr(compiled, t.name)
        inst = cls(**generate_type_kwargs(t, 1))
        for p in t.fields:
            signal = getattr(inst, p.signal_name)
            with qtbot.wait_signal(signal):
                getattr(inst, p.setter_name)(2)
            assert getattr(inst, p.name) == 2
