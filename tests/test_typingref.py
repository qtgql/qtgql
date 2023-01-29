from typing import Generic, List, Optional, TypeVar, Union, get_args, get_origin

import pytest
from qtgql.typingref import UNSET, TypeHinter, UnsetType


class TestFromAnnotation:
    @pytest.mark.parametrize("tp", [int, float, str, bool, object])
    def test_simple_type(self, tp):
        th = TypeHinter.from_annotations(tp)
        assert th.type is tp

    @pytest.mark.parametrize("tp", [list[float], Optional[str]])
    def test_containers(self, tp):
        th = TypeHinter.from_annotations(tp)
        assert th.type is get_origin(tp)
        assert th.of_type[0].type is get_args(tp)[0]

    def test_unions(self):
        tp = Union[str, int]
        th = TypeHinter.from_annotations(tp)
        assert th.type is get_origin(tp)
        for index, type_ in enumerate(th.of_type):
            assert type_.type is get_args(tp)[index]

    def test_nested(self):
        tp = list[Union[str, int]]
        th = TypeHinter.from_annotations(tp)
        assert th.type is list
        assert th.of_type[0].type is Union
        assert th.of_type[0].of_type[0].type is str
        assert th.of_type[0].of_type[1].type is int


class TestToAnnotation:
    @pytest.mark.parametrize("tp", [int, float, str, bool, object])
    def test_builtins(self, tp):
        th = TypeHinter(type=tp, of_type=tuple())
        assert th.as_annotation() == tp

    @pytest.mark.parametrize(
        "container, inner", [(list, float), (Optional, str), (List, int), (tuple, bool)]
    )
    def test_containers(self, container, inner):
        th = TypeHinter(type=container, of_type=(TypeHinter(type=inner),))
        assert th.as_annotation() == container[inner]

    def test_unions(self):
        tp = Union[str, int]
        th = TypeHinter(type=Union, of_type=(TypeHinter(str), TypeHinter(int)))
        assert th.as_annotation() == tp

    def test_nested(self):
        tp = list[Union[str, int]]
        th = TypeHinter(
            type=list,
            of_type=(TypeHinter(type=Union, of_type=(TypeHinter(type=str), TypeHinter(type=int))),),
        )

        assert th.as_annotation() == tp

    def test_forward_refs(self):
        class SomeHiddenType:
            ...

        tp = Optional[SomeHiddenType]
        th = TypeHinter(type=Optional, of_type=(TypeHinter(type=SomeHiddenType.__name__),))
        assert th.as_annotation({SomeHiddenType.__name__: SomeHiddenType}) == tp


class TestFromString:
    @pytest.mark.parametrize("tp", [int, float, str, bool, object])
    def test_builtins(self, tp):
        assert TypeHinter.from_string(tp.__name__, ns={}).type == tp

    @pytest.mark.parametrize(
        "container, inner", [(list, float), (Optional, str), (List, int), (tuple, bool)]
    )
    def test_containers(self, container, inner):
        def as_str():
            return container.__name__ + "[" + inner.__name__ + "]"

        th = TypeHinter.from_string(as_str(), ns={})
        assert th == TypeHinter.from_annotations(container[inner])

    def test_user_type(self):
        class MyType:
            ...

        assert TypeHinter.from_string("MyType", ns=locals()).type is MyType

    def test_generic_types(self):
        T = TypeVar("T")

        class A(Generic[T]):
            ...

        assert TypeHinter.from_string("A", ns=locals()).type is A


class TestUnsetType:
    def test_returns_null_str(self):
        assert not str(UNSET)

    def test_false_bool(self):
        assert not bool(UNSET)

    def test_singleton(self):
        assert UNSET is UnsetType()


def test_is_union():
    th = TypeHinter.from_annotations(Union[str, int])
    assert th.is_union()
    th = TypeHinter.from_annotations(int)
    assert not th.is_union()


def test_is_optional():
    th = TypeHinter.from_annotations(Optional[str])
    assert th.is_optional()
    th = TypeHinter.from_annotations(int)
    assert not th.is_optional()
