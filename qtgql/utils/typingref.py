import inspect
from typing import Any, List, Optional, Type, TypeVar, Union, get_args, get_origin


class UnsetType:
    __instance: Optional["UnsetType"] = None

    def __new__(cls: Type["UnsetType"]) -> "UnsetType":
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            return cls.__instance
        return cls.__instance

    def __str__(self):
        return ""

    def __repr__(self) -> str:  # pragma: no cover
        return "UNSET"

    def __bool__(self):
        return False


UNSET: Any = UnsetType()


class TypeHinter:
    def __init__(
        self,
        type: Any,
        of_type: tuple["TypeHinter", ...] = (),
    ):
        self.type = type
        self.of_type = of_type

    def __eq__(self, other) -> bool:
        if not isinstance(other, TypeHinter):
            return False

        if not self.type == other.type:
            return False

        return all(child == other.of_type[count] for count, child in enumerate(self.of_type))

    @classmethod
    def from_string(cls, tp: str, ns: dict) -> "TypeHinter":
        from typing import List, Union, Dict, Optional, Any, Type, get_type_hints  # noqa

        ns = ns.copy()
        ns.update(locals())

        def tmp(t: tp):  # type: ignore
            ...  # pragma: no cover

        annotation = get_type_hints(tmp, localns=ns, globalns=globals())["t"]

        return cls.from_annotations(annotation)

    @classmethod
    def from_annotations(cls, tp: Any) -> "TypeHinter":
        if args := get_args(tp):
            # handle optional
            if type(None) in args:
                # optional union, 2 is default for optionals
                if len(args) > 2:
                    return cls(
                        type=Optional,
                        of_type=(
                            cls(
                                type=Union,
                                of_type=tuple(
                                    cls.from_annotations(arg)
                                    for arg in args
                                    if arg is not type(None)
                                ),
                            ),
                        ),
                    )
                return cls(type=Optional, of_type=(cls.from_annotations(args[0]),))
            new_args: list[TypeHinter] = []
            for arg in args:
                new_args.append(cls.from_annotations(arg))

            return cls(type=get_origin(tp), of_type=tuple(new_args))  # type: ignore
        return cls(type=tp)

    def as_annotation(self, object_map: Optional[dict[str, Any]] = None) -> Any:
        if self.type is str:
            return self.type
        # eval forward refs
        if isinstance(self.type, str):
            assert object_map, "can't evaluate forward refs without object_map."
            self.type = object_map[self.type]

        if builder := getattr(
            self.type, "__class_getitem__", getattr(self.type, "__getitem__", None)
        ):
            if self.is_union():
                return builder(tuple(arg.as_annotation(object_map) for arg in self.of_type))
            return builder(self.of_type[0].as_annotation(object_map))
        return self.type

    def stringify(self) -> str:
        annot = self.as_annotation()
        if inspect.isclass(annot) and not hasattr(annot, "__origin__"):
            return annot.__name__

        return str(annot).replace("typing.", "").replace("qtgql.codegen.utils.", "")

    def is_union(self) -> bool:
        return self.type is Union

    def is_optional(self) -> bool:
        return self.type is Optional

    def is_list(self) -> bool:
        return self.type in (list, List)

    @classmethod
    def strip_optionals(cls, inst: "TypeHinter") -> "TypeHinter":
        th = inst
        if inst.is_optional():
            th = inst.of_type[0]

        return cls(type=th.type, of_type=tuple(cls.strip_optionals(tp) for tp in th.of_type))


T = TypeVar("T")


def ensure(inst: T, tp: Type[T]) -> T:
    if not isinstance(inst, tp):
        raise TypeError(f"{inst} is not of type {tp}")
    return inst
