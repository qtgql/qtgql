from qtgql.itemsystem import GenericModel, role

from tests.test_itemsystem.conftest import FullClass, init_dict_fullClass


def test_has_inner_class_GenericModel(full_model):
    t = full_model.type_
    assert t is FullClass
    assert issubclass(t.Model, GenericModel)


def test_initialize():
    FullClass(**init_dict_fullClass())


def test_post_init(base_type):
    class WithPostInit(base_type):
        unit_name: int = role(default=4)

        def __attrs_post_init__(self):
            self.unit_name = 2

    assert WithPostInit().unit_name == 2
