from enum import Enum

from tests.test_codegen.schemas import object_with_enum
from tests.test_codegen.test_py.test_introspection_generator import EnumTestCase


def test_generates_valid_python_enum():
    EnumTestCase.compile()
    generated_enum = EnumTestCase.module.Status
    assert issubclass(generated_enum, Enum)
    for member in object_with_enum.Status:
        assert generated_enum(member.value).name == member.name


def test_accessible_from_qml():
    raise NotImplementedError
