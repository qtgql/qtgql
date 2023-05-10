from __future__ import annotations

from collections import defaultdict
from functools import cached_property
from textwrap import dedent
from typing import Optional
from typing import TYPE_CHECKING

import attrs
from attr import define
from frozendict import frozendict
from typingref import UNSET

from qtgqlcodegen.compiler.template import config_template
from qtgqlcodegen.compiler.template import ConfigContext
from qtgqlcodegen.graphql_ref import has_id_selection
from qtgqlcodegen.graphql_ref import has_typename_selection
from qtgqlcodegen.graphql_ref import inject_id_selection
from qtgqlcodegen.graphql_ref import inject_typename_selection
from qtgqlcodegen.graphql_ref import is_field_node
from qtgqlcodegen.graphql_ref import is_inline_fragment


if TYPE_CHECKING:
    from graphql import language as gql_lang, OperationType

    from qtgqlcodegen.introspection import SchemaEvaluator
    from qtgqlcodegen.objecttype import QtGqlVariableDefinition, GqlTypeHinter
    from qtgqlcodegen.objecttype import QtGqlFieldDefinition
    from qtgqlcodegen.objecttype import QtGqlObjectTypeDefinition


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


@attrs.define(frozen=True)
class QtGqlQueriedField:
    definition: QtGqlFieldDefinition
    choices: frozendict[str, dict[str, QtGqlQueriedField]] = attrs.Factory(frozendict)
    selections: dict[str, QtGqlQueriedField] = attrs.Factory(dict)

    @property
    def type(self) -> GqlTypeHinter:
        return self.definition.type

    @property
    def name(self) -> str:
        return self.definition.name

    @property
    def ctype(self) -> str:
        return self.definition.type.annotation

    def __hash__(self) -> int:
        return hash((hash(self.selections), hash(self.choices), self.definition.name))

    @classmethod
    def from_field(
        cls,
        field_definition: QtGqlFieldDefinition,
        selection_set: Optional[gql_lang.SelectionSetNode],
        schema_evaluator: SchemaEvaluator,
        parent_interface_field: Optional[QtGqlQueriedField] = UNSET,
    ) -> QtGqlQueriedField:
        """Main purpose here is to find inner selections of fields, this could
        be an object type, interface, union or a list.

        Any other fields should not have inner selections.
        """
        assert parent_interface_field is not UNSET
        if not hasattr(selection_set, "selections"):
            return cls(definition=field_definition)
        assert selection_set
        tp = field_definition.type
        if (
            tp.is_model
        ):  # GraphQL's lists are basically the object beneath them in terms of selections.
            tp = tp.is_model

        tp_is_union = tp.is_union

        # inject id selection for types that supports it. unions are handled below.
        if field_definition.can_select_id and not has_id_selection(selection_set):
            inject_id_selection(selection_set)

        selections: dict[str, QtGqlQueriedField] = {}
        choices: defaultdict[str, dict[str, QtGqlQueriedField]] = defaultdict(dict)
        # inject parent interface selections.
        if (tp.is_object_type or tp.is_interface) and parent_interface_field:
            selections.update({f.name: f for f in parent_interface_field.selections})

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
                        __f = get_field_from_field_node(
                            field_node,
                            concrete,
                            schema_evaluator,
                            parent_interface_field,
                        )
                        choices[type_name][field_definition.name] = __f

        elif interface_def := tp.is_interface:
            # first get all linear selections.
            for selection in selection_set.selections:
                if not is_inline_fragment(selection):
                    field_node = is_field_node(selection)
                    assert field_node
                    if not is_type_name_selection(field_node):
                        __f = get_field_from_field_node(
                            field_node,
                            interface_def,
                            schema_evaluator,
                            parent_interface_field,
                        )
                        selections[__f.name] = __f

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
                            __f = get_field_from_field_node(
                                field_node,
                                concrete,
                                schema_evaluator,
                                parent_interface_field,
                            )
                            choices[type_name][field_definition.name] = __f

        else:  # object types.
            obj_def = tp.is_object_type
            assert obj_def
            for selection in selection_set.selections:
                field_node = is_field_node(selection)
                assert field_node
                if not is_type_name_selection(field_node):
                    __f = get_field_from_field_node(
                        field_node,
                        obj_def,
                        schema_evaluator,
                        parent_interface_field,
                    )
                    selections[__f.name] = __f

        def sorted_distinct_fields(
            fields: dict[str, QtGqlQueriedField],
        ) -> dict[str, QtGqlQueriedField]:
            return dict(sorted(fields.items()))

        return cls(
            definition=field_definition,
            selections=sorted_distinct_fields(selections),
            choices=frozendict({k: sorted_distinct_fields(v) for k, v in choices.items()}),
        )

    def as_conf_string(self) -> str:
        return dedent(
            config_template(
                context=ConfigContext(self),
            ),
        )


@define(slots=False)
class QtGqlQueriedObjectType:
    definition: QtGqlObjectTypeDefinition = attrs.field(on_setattr=attrs.setters.frozen)
    fields: dict[str, QtGqlQueriedField] = attrs.Factory(dict)

    @cached_property
    def name(self) -> str:
        return f"{self.definition.name}__{'$'.join(self.fields.keys())}"

    @cached_property
    def doc_fields(self) -> str:
        return "{} {{\n  {}\n}}".format(
            self.definition.name,
            "\n   ".join(self.fields.keys()),
        )


@define(slots=False)
class QtGqlOperationDefinition:
    query: str
    name: str
    root_type: QtGqlObjectTypeDefinition
    operation_kind: OperationType
    field: QtGqlQueriedField
    directives: list[str] = []
    fragments: list[str] = []
    variables: list[QtGqlVariableDefinition] = []

    @property
    def operation_config(self) -> str:
        return self.field.as_conf_string()

    @cached_property
    def narrowed_types(self) -> tuple[QtGqlQueriedObjectType]:
        ret: dict[str, QtGqlQueriedObjectType] = {}

        def recurse(f: QtGqlQueriedField):
            field_type = f.definition.type.is_object_type
            assert field_type
            obj = QtGqlQueriedObjectType(
                definition=field_type,
                fields=f.selections,
            )
            # even though one type could have been queried the same at one level but differently
            # on deeper levels we don't need to distinguish between them since
            # these should just be a proxy object of the real instance.
            if obj.name not in ret.keys():
                ret[obj.name] = obj

            # we still need to recurse deeper in that field though.
            for selection in f.selections.values():
                if selection.definition.type.is_object_type:
                    recurse(selection)

        recurse(self.field)
        return tuple(ret.values())
