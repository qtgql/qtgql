from __future__ import annotations

from collections import defaultdict
from textwrap import dedent
from typing import TYPE_CHECKING, List, NamedTuple, Optional

import attrs

from qtgql.codegen.graphql_ref import is_field_node, is_inline_fragment
from qtgql.codegen.py.compiler.template import (
    ConfigContext,
    config_template,
)
from qtgql.codegen.py.objecttype import GqlFieldDefinition, GqlTypeDefinition
from qtgql.codegen.utils import AntiForwardRef

if TYPE_CHECKING:
    from graphql import language as gql_lang


def get_field_from_field_node(
    selection: gql_lang.FieldNode, field_type: GqlTypeDefinition
) -> QtGqlQueriedField:
    field_node = is_field_node(selection)
    assert field_node
    return QtGqlQueriedField.from_field(
        field_type.fields_dict[field_node.name.value], selection_set=field_node.selection_set
    )


@attrs.define
class QtGqlQueriedField(GqlFieldDefinition):
    # TODO: rename this to selections
    selections: List[QtGqlQueriedField] = attrs.Factory(list)
    choices: dict[str, List[QtGqlQueriedField]] = attrs.Factory(lambda: defaultdict(list))

    @classmethod
    def from_field(
        cls, f: GqlFieldDefinition, selection_set: Optional[gql_lang.SelectionSetNode]
    ) -> QtGqlQueriedField:
        ret = cls(**attrs.asdict(f, recurse=False))
        if not hasattr(selection_set, "selections"):
            return ret
        assert selection_set
        for selection in selection_set.selections:
            if inline_frag := is_inline_fragment(selection):
                assert ret.type.is_union()  # ATM supported fragments are unions only.
                type_name = inline_frag.type_condition.name.value
                concrete = next(t for t in f.type.of_type if t.type.name == type_name)
                assert issubclass(concrete.type, AntiForwardRef)
                concrete = concrete.type.resolve()
                assert isinstance(concrete, GqlTypeDefinition)
                for selection_node in inline_frag.selection_set.selections:
                    field_node = is_field_node(selection_node)
                    assert field_node
                    if field_node.name.value == "__typename":
                        continue
                    ret.choices[type_name].append(get_field_from_field_node(field_node, concrete))
            else:
                f_type = f.type.is_object_type
                if not f_type:
                    f_type = f.type.is_model
                assert f_type
                field_node = is_field_node(selection)
                assert field_node
                ret.selections.append(get_field_from_field_node(field_node, f_type))
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
