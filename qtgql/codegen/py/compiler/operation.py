from __future__ import annotations

from collections import defaultdict
from textwrap import dedent
from typing import NamedTuple
from typing import Optional
from typing import TYPE_CHECKING

import attrs
from typingref import UNSET

from qtgql.codegen.graphql_ref import has_id_selection
from qtgql.codegen.graphql_ref import has_typename_selection
from qtgql.codegen.graphql_ref import inject_id_selection
from qtgql.codegen.graphql_ref import inject_typename_selection
from qtgql.codegen.graphql_ref import is_field_node
from qtgql.codegen.graphql_ref import is_inline_fragment
from qtgql.codegen.py.compiler.template import config_template
from qtgql.codegen.py.compiler.template import ConfigContext
from qtgql.codegen.py.objecttype import QtGqlFieldDefinition
from qtgql.codegen.py.objecttype import QtGqlObjectTypeDefinition

if TYPE_CHECKING:
    from graphql import language as gql_lang

    from qtgql.codegen.introspection import SchemaEvaluator
    from qtgql.codegen.py.objecttype import QtGqlVariableDefinition


def is_type_name_selection(field_node: gql_lang.FieldNode):
    # typename is not a 'real' selection and is handled with special care.
    if field_node.name.value == "__typename":
        return True
    return False


def get_field_from_field_node(
    selection: gql_lang.FieldNode,
    field_type: QtGqlObjectTypeDefinition,
    schema_evaluator: SchemaEvaluator,
    parent_interface_field: Optional[QtGqlQueriedField] = UNSET,
) -> QtGqlQueriedField:
    field_node = is_field_node(selection)
    assert field_node
    return QtGqlQueriedField.from_field(
        field_type.fields_dict[field_node.name.value],
        selection_set=field_node.selection_set,
        schema_evaluator=schema_evaluator,
        parent_interface_field=parent_interface_field,
    )


class UniqueFieldsList(list["QtGqlQueriedField"]):
    def append(self, obj: QtGqlQueriedField) -> None:
        for v in self:
            if v.name == obj.name:
                pass
        super().append(obj)

    def extend(self, other) -> None:
        for v in other:
            self.append(v)


@attrs.define
class QtGqlQueriedField(QtGqlFieldDefinition):
    selections: UniqueFieldsList = attrs.Factory(UniqueFieldsList)
    choices: dict[str, UniqueFieldsList] = attrs.Factory(lambda: defaultdict(UniqueFieldsList))

    @classmethod
    def from_field(
        cls,
        f: QtGqlFieldDefinition,
        selection_set: Optional[gql_lang.SelectionSetNode],
        schema_evaluator: SchemaEvaluator,
        parent_interface_field: Optional[QtGqlQueriedField] = UNSET,
    ) -> QtGqlQueriedField:
        """Main purpose here is to find inner selections of fields, this could
        be an object type, interface, union or a list.

        Any other fields should not have inner selections.
        """
        assert parent_interface_field is not UNSET
        ret = cls(**attrs.asdict(f, recurse=False))
        if not hasattr(selection_set, "selections"):
            return ret
        assert selection_set
        tp = ret.type
        if (
            tp.is_model
        ):  # GraphQL's lists are basically the object beneath them in terms of selections.
            tp = tp.strip_optionals(tp)
            tp = tp.of_type[0]

        tp_is_union = tp.is_union

        # inject id selection for types that supports it. unions are handled below.
        if f.can_select_id and not has_id_selection(selection_set):
            inject_id_selection(selection_set)

        # inject parent interface selections.
        if (tp.is_object_type or tp.is_interface) and parent_interface_field:
            ret.selections.extend(parent_interface_field.selections)

        if tp_is_union:
            for selection in selection_set.selections:
                fragment = is_inline_fragment(selection)
                assert fragment

                type_name = fragment.type_condition.name.value
                concrete = schema_evaluator.get_objecttype_by_name(type_name)
                assert concrete
                if not has_typename_selection(fragment.selection_set):
                    inject_typename_selection(fragment.selection_set)
                if not has_id_selection(fragment.selection_set) and concrete.has_id_field:
                    inject_id_selection(fragment.selection_set)

                for selection_node in fragment.selection_set.selections:
                    field_node = is_field_node(selection_node)
                    assert field_node

                    if not is_type_name_selection(field_node):
                        ret.choices[type_name].append(
                            get_field_from_field_node(
                                field_node,
                                concrete,
                                schema_evaluator,
                                parent_interface_field,
                            ),
                        )

        elif interface_def := tp.is_interface:
            # first get all linear selections.
            for selection in selection_set.selections:
                if not is_inline_fragment(selection):
                    field_node = is_field_node(selection)
                    assert field_node
                    if not is_type_name_selection(field_node):
                        ret.selections.append(
                            get_field_from_field_node(
                                field_node,
                                interface_def,
                                schema_evaluator,
                                parent_interface_field,
                            ),
                        )

            for selection in selection_set.selections:
                if inline_frag := is_inline_fragment(selection):
                    type_name = inline_frag.type_condition.name.value
                    # no need to validate inner types are implementation, graphql-core does this.
                    concrete = schema_evaluator.get_objecttype_by_name(
                        type_name,
                    ) or schema_evaluator.get_interface_by_name(type_name)
                    assert concrete
                    for inner_selection in inline_frag.selection_set.selections:
                        field_node = is_field_node(inner_selection)
                        assert field_node
                        if not is_type_name_selection(field_node):
                            ret.choices[type_name].append(
                                get_field_from_field_node(
                                    field_node,
                                    concrete,
                                    schema_evaluator,
                                    parent_interface_field,
                                ),
                            )

        else:  # object types.
            obj_def = tp.is_object_type
            assert obj_def
            for selection in selection_set.selections:
                field_node = is_field_node(selection)
                assert field_node
                if not is_type_name_selection(field_node):
                    ret.selections.append(
                        get_field_from_field_node(
                            field_node,
                            obj_def,
                            schema_evaluator,
                            parent_interface_field,
                        ),
                    )
        return ret

    def as_conf_string(self) -> str:
        return dedent(
            config_template(
                context=ConfigContext(self),
            ),
        )


class QtGqlOperationDefinition(NamedTuple):
    query: str
    name: str
    operation_type: QtGqlObjectTypeDefinition
    field: QtGqlQueriedField
    directives: list[str] = []
    fragments: list[str] = []
    variables: list[QtGqlVariableDefinition] = []

    @property
    def operation_config(self) -> str:
        return self.field.as_conf_string()
