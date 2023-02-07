from typing import Generic, List, Optional, TypeVar, Union, get_args, get_origin

import pytest
from qtgql.typingref import UNSET, TypeHinter, UnsetType, ensure


class TestFromAnnotation:
    @pytest.mark.parametrize("tp", [int, float, str, bool, object])
    def test_simple_type(self, tp):
        th = TypeHinter.from_annotations(tp)
        assert th.type is tp

    @pytest.mark.parametrize("tp", [list[float], Optional[str]])
    def test_containers(self, tp):
        th = TypeHinter.from_annotations(tp)
        assert th.type[get_args(tp)[0]] == tp
        assert th.of_type[0].type is get_args(tp)[0]

    def test_unions(self):
        tp = Union[str, int]
        th = TypeHinter.from_annotations(tp)
        assert th.type is get_origin(tp)
        for index, type_ in enumerate(th.of_type):
            assert type_.type is get_args(tp)[index]

    def test_union_with_optionals(self):
        """Union with one optional basically means that the type is the union
        is optional."""
        tp = Union[Optional[str], Optional[int]]
        th = TypeHinter.from_annotations(tp)
        assert th.type is Optional
        inner = th.of_type[0]
        assert inner.of_type[0].type is str
        assert inner.of_type[1].type is int

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
            try:
                cont_name = container.__name__
            except AttributeError:  # in python 3.9 `Optional` is not a class.
                cont_name = str(container).replace("typing.", "")
            return cont_name + "[" + inner.__name__ + "]"

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


@pytest.mark.parametrize("list_class", (list, List))
def test_is_list(list_class):
    th = TypeHinter.from_annotations(list_class[int])
    assert th.is_list()
    th = TypeHinter.from_annotations(int)
    assert not th.is_list()


def test_is_optional():
    th = TypeHinter.from_annotations(Optional[str])
    assert th.is_optional()
    th = TypeHinter.from_annotations(int)
    assert not th.is_optional()


class TestStringify:
    @pytest.mark.parametrize("tp", [int, float, str, bool, object])
    def test_builtins(self, tp):
        assert TypeHinter.from_annotations(tp).stringify() == tp.__name__

    @pytest.mark.parametrize(
        "expected", ["List[int]", "Optional[str]", "list[float]", "tuple[bool]"]
    )
    def test_containers(self, expected):
        assert TypeHinter.from_string(expected, {}).stringify() in (expected, expected.lower())


class TestStripOptionals:
    def test_flat(self):
        th = TypeHinter.strip_optionals(TypeHinter.from_annotations(Optional[str]))
        assert th.type is str

    def test_inner_optional(self):
        th = TypeHinter.strip_optionals(TypeHinter.from_annotations(list[Optional[str]]))

        assert th.type is list
        assert th.of_type[0].type is str

    def test_union(self):
        th = TypeHinter.from_annotations(Union[Optional[str], Optional[int], float])
        th = TypeHinter.strip_optionals(th)
        assert th.of_type[0].type is str
        assert th.of_type[1].type is int
        assert th.of_type[2].type is float


class TestCompare:
    def test_ne(self):
        assert TypeHinter.from_annotations(str) != TypeHinter.from_annotations(int)

    def test_eq(self):
        assert TypeHinter.from_annotations(str) == TypeHinter.from_annotations(str)

    def test_nested_ne(self):
        assert TypeHinter.from_annotations(list[str]) != TypeHinter.from_annotations(list[int])

    def test_nested_eq(self):
        assert TypeHinter.from_annotations(list[str]) == TypeHinter.from_annotations(list[str])


def test_ensure_success():
    hello = "hello"
    assert ensure(hello, str) == hello


def test_ensure_fails():
    with pytest.raises(TypeError):
        ensure("hello", int)
