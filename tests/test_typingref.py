from typing import Optional, Union, get_args, get_origin

import pytest

from qtgql.typingref import TypeHinter


class TestRoleType:
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
