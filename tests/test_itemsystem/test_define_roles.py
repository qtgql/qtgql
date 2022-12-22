from qtgql.itemsystem import BaseRoleDefined, GenericModel, role
from tests.test_itemsystem.fixtures import FullClass, WithChild, init_dict_fullClass


def test_has_dunder_roles():
    assert hasattr(FullClass, "__roles__")


def test_first_role_is_256():
    assert list(FullClass.__roles__.qt_roles.keys())[0] == 256


def test_role_fields_in_qt_roles():
    roles = FullClass.__roles__
    qt_roles = roles.qt_roles
    for num, role_ in roles.by_num.items():
        assert role_.qt_name is qt_roles[num]


def test_roledefined_with_children_collects_them():
    roles = WithChild.__roles__
    assert roles.children
    assert roles.children["child"].type.of_type[0].type is FullClass


def test_get_subclassed_model():
    assert issubclass(FullClass.Model, GenericModel)


def test_initialize():
    FullClass(**init_dict_fullClass())


def test_post_init():
    class WithPostInit(BaseRoleDefined):
        unit_name: int = role(init=False, default=4)

        def __attrs_post_init__(self):
            self.unit_name = 2

    assert WithPostInit().unit_name == 2
