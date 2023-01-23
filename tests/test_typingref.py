from typing import List, Optional, Union, get_args, get_origin

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
    def test_simple_type(self, tp):
        th = TypeHinter(type=tp, of_type=tuple())
        assert th.as_annotation() == tp

    @pytest.mark.parametrize(
        "container, inner", [(list, float), (Optional, str), (List, int), (tuple, bool)]
    )
    def test_containers(self, container, inner):
        th = TypeHinter(type=container, of_type=(TypeHinter(type=inner, of_type=None),))
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


class TestUnsetType:
    def test_returns_null_str(self):
        assert not str(UNSET)

    def test_false_bool(self):
        assert not bool(UNSET)

    def test_singleton(self):
        assert UNSET is UnsetType()
