from enum import Enum
from textwrap import dedent

import pytest
from PySide6.QtCore import QObject

from tests.test_codegen.schemas import object_with_enum
from tests.test_codegen.test_py.testcases import EnumTestCase


def test_generates_valid_python_enum():
    testcase = EnumTestCase.compile()
    generated_enum = testcase.objecttypes_mod.Status
    assert issubclass(generated_enum, Enum)
    for member in object_with_enum.Status:
        assert generated_enum(member.value).name == member.name


def test_generates_qobject_class_with_all_the_enums():
    testcase = EnumTestCase.compile()
    mod = testcase.objecttypes_mod
    assert issubclass(mod.Enums, QObject)
    assert mod.Enums
    assert mod.Enums.Status is mod.Status


@pytest.mark.parametrize("status", iter(object_with_enum.Status))
def test_accessible_from_qml(qmlbot, status):
    qml = dedent(
        """
        import QtQuick
        import generated.TestEnv.types as Env

        Rectangle {
            objectName: "rootObject"
            property int enumValue: Env.Enums.%s
        }


        """
        % status.name
    )

    EnumTestCase.compile()
    item = qmlbot.loads(qml)
    assert item.property("enumValue") == status.value
