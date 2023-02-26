from __future__ import annotations

from collections import defaultdict
from textwrap import dedent
from typing import TYPE_CHECKING, List, NamedTuple

import attrs

from qtgql.codegen.graphql_ref import is_field_node, is_inline_fragment
from qtgql.codegen.py.compiler.template import (
    ConfigContext,
    config_template,
)
from qtgql.codegen.py.objecttype import GqlFieldDefinition
from qtgql.codegen.utils import AntiForwardRef

if TYPE_CHECKING:
    from graphql import language as gql_lang

    from qtgql.codegen.py.objecttype import GqlTypeDefinition


def get_field_from_field_node(
    selection: gql_lang.FieldNode, field_type: GqlTypeDefinition
) -> QtGqlQueriedField:
    field_node = is_field_node(selection)
    assert is_field_node
    return QtGqlQueriedField.from_field(
        field_type.fields_dict[field_node.name.value], selection_set=field_node.selection_set
    )


@attrs.define
class QtGqlQueriedField(GqlFieldDefinition):
    # TODO: rename this to selections
    selection_set: List[QtGqlQueriedField] = attrs.Factory(list)
    choices: dict[str, List[QtGqlQueriedField]] = attrs.Factory(lambda: defaultdict(list))

    @classmethod
    def from_field(
        cls, f: GqlFieldDefinition, selection_set: gql_lang.SelectionSetNode
    ) -> QtGqlQueriedField:
        ret = cls(**attrs.asdict(f, recurse=False))
        if not hasattr(selection_set, "selections"):
            return ret
        for selection in selection_set.selections:
            if inline_frag := is_inline_fragment(selection):
                assert ret.type.is_union()  # ATM supported fragments are unions only.
                type_name = inline_frag.type_condition.name.value
                concrete = next(t for t in f.type.of_type if t.type.name == type_name)
                assert issubclass(concrete.type, AntiForwardRef)
                concrete = concrete.type.resolve()
                for field_node in inline_frag.selection_set.selections:
                    field_node = is_field_node(field_node)
                    if field_node.name.value == "__typename":
                        continue
                    ret.choices[type_name].append(get_field_from_field_node(field_node, concrete))
            else:
                f_type = f.type.is_object_type
                if not f_type:
                    f_type = f.type.is_model
                assert f_type
                ret.selection_set.append(get_field_from_field_node(selection, f_type))
        return ret

    def as_conf_string(self) -> str:
        return dedent(
            config_template(
                context=ConfigContext(self),
            )
        )


class QtGqlQueryHandlerDefinition(NamedTuple):
    query: str
    name: str
    field: QtGqlQueriedField
    directives: list[str] = []
    fragments: list[str] = []

    @property
    def operation_config(self) -> str:
        return self.field.as_conf_string()
