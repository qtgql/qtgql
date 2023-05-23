from __future__ import annotations

from collections import defaultdict
from functools import cached_property
from typing import Optional
from typing import TYPE_CHECKING

import attrs
import graphql
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
    from graphql import language as gql_lang
    from graphql.type import definition as gql_def

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
    operation: QtGqlOperationDefinition,
    parent_interface_field: Optional[QtGqlQueriedField] = UNSET,
) -> QtGqlQueriedField:
    field_node = is_field_node(selection)
    assert field_node
    return QtGqlQueriedField.from_field(
        field_type.fields_dict[field_node.name.value],
        selection_set=field_node.selection_set,
        operation=operation,
        parent_interface_field=parent_interface_field,
    )


@attrs.define(frozen=True, slots=False)
class QtGqlQueriedField:
    definition: QtGqlFieldDefinition
    operation: QtGqlOperationDefinition
    choices: frozendict[str, dict[str, QtGqlQueriedField]] = attrs.Factory(frozendict)
    selections: dict[str, QtGqlQueriedField] = attrs.Factory(dict)
    narrowed_type: Optional[QtGqlQueriedObjectType] = None

    def __repr__(self):
        return (
            f"{self.definition.name}[{', '.join(self.selections.keys())}\n"
            + "...on".join([f"{k} {repr(v)}" for k, v in self.choices.items()])
            + "]"
        )

    @cached_property
    def type(self) -> GqlTypeHinter:
        return self.definition.type

    @cached_property
    def property_type(self) -> str:
        if self.definition.type.is_object_type:
            assert self.narrowed_type
            return self.narrowed_type.name
        if cs := self.definition.is_custom_scalar:
            return cs.property_type
        return self.type.member_type

    @property
    def proxy_of(self) -> GqlTypeHinter:
        ret = self.definition.type
        assert ret
        return ret

    @property
    def name(self) -> str:
        return self.definition.name

    @classmethod
    def from_field(
        cls,
        field_definition: QtGqlFieldDefinition,
        selection_set: Optional[gql_lang.SelectionSetNode],
        operation: QtGqlOperationDefinition,
        parent_interface_field: Optional[QtGqlQueriedField] = UNSET,
    ) -> QtGqlQueriedField:
        """Main purpose here is to find inner selections of fields, this could
        be an object type, interface, union or a list.

        Any other fields should not have inner selections.
        """
        assert parent_interface_field is not UNSET
        if not hasattr(selection_set, "selections"):
            return cls(definition=field_definition, operation=operation)
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
        narrowed_type: Optional[QtGqlQueriedObjectType] = None
        # inject parent interface selections.
        if (tp.is_object_type or tp.is_interface) and parent_interface_field:
            selections.update({f.name: f for f in parent_interface_field.selections.values()})

        if tp_is_union:
            for selection in selection_set.selections:
                fragment = is_inline_fragment(selection)
                assert fragment

                type_name = fragment.type_condition.name.value
                concrete = operation.evaluator.get_objecttype_by_name(type_name)
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
                            operation,
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
                            operation,
                            parent_interface_field,
                        )
                        selections[__f.name] = __f

            for selection in selection_set.selections:
                if inline_frag := is_inline_fragment(selection):
                    type_name = inline_frag.type_condition.name.value
                    # no need to validate inner types are implementation, graphql-core does this.
                    concrete = operation.evaluator.get_objecttype_by_name(
                        type_name,
                    ) or operation.evaluator.get_interface_by_name(type_name)
                    assert concrete
                    for inner_selection in inline_frag.selection_set.selections:
                        field_node = is_field_node(inner_selection)
                        assert field_node
                        if not is_type_name_selection(field_node):
                            __f = get_field_from_field_node(
                                field_node,
                                concrete,
                                operation,
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
                        operation,
                        parent_interface_field,
                    )
                    selections[__f.name] = __f
            queried_obj = QtGqlQueriedObjectType(
                definition=obj_def,
                fields=selections,
            )
            operation.narrowed_types_map[queried_obj.name] = queried_obj
            narrowed_type = queried_obj

        def sorted_distinct_fields(
            fields: dict[str, QtGqlQueriedField],
        ) -> dict[str, QtGqlQueriedField]:
            return dict(sorted(fields.items()))

        return cls(
            definition=field_definition,
            selections=sorted_distinct_fields(selections),
            choices=frozendict({k: sorted_distinct_fields(v) for k, v in choices.items()}),
            operation=operation,
            narrowed_type=narrowed_type,
        )

    def as_conf_string(self) -> str:
        return config_template(
            context=ConfigContext(self),
        )


@define(slots=False)
class QtGqlQueriedObjectType:
    definition: QtGqlObjectTypeDefinition = attrs.field(on_setattr=attrs.setters.frozen)
    fields: dict[str, QtGqlQueriedField] = attrs.Factory(dict)

    @cached_property
    def name(self) -> str:
        return f"{self.definition.name}__{'$'.join(sorted(self.fields.keys()))}"

    @cached_property
    def doc_fields(self) -> str:
        return "{} {{\n  {}\n}}".format(
            self.definition.name,
            "\n   ".join(self.fields.keys()),
        )


@define(slots=False)
class QtGqlOperationDefinition:
    operation_def: gql_def.OperationDefinitionNode
    evaluator: SchemaEvaluator
    directives: list[str] = attrs.Factory(list)
    fragments: list[str] = attrs.Factory(list)
    variables: list[QtGqlVariableDefinition] = attrs.Factory(list)
    narrowed_types_map: dict[str, QtGqlQueriedObjectType] = attrs.Factory(dict)

    def __attrs_post_init__(self) -> None:
        # instantiating the queried fields here, they build the narrowed types.
        self.root_field  # noqa

    @property
    def operation_config(self) -> str:
        return self.root_field.as_conf_string()

    @property
    def name(self) -> str:
        assert self.operation_def.name
        return self.operation_def.name.value

    @cached_property
    def query(self) -> str:
        return graphql.print_ast(self.operation_def)

    @cached_property
    def narrowed_types(self) -> tuple[QtGqlQueriedObjectType, ...]:
        return tuple(self.narrowed_types_map.values())

    @cached_property
    def _root_type(self) -> QtGqlObjectTypeDefinition:
        root_type = self.evaluator.operation_types.get(self.operation_def.operation, None)
        assert root_type, f"You don't have a {self.operation_def.operation} type on your schema"
        return root_type

    @cached_property
    def root_field(self) -> QtGqlQueriedField:
        root_field_def: gql_lang.FieldNode = self.operation_def.selection_set.selections[0]  # type: ignore
        return QtGqlQueriedField.from_field(
            self._root_type.fields_dict[root_field_def.name.value],
            root_field_def.selection_set,
            self,
            parent_interface_field=None,
        )

    @classmethod
    def from_definition(
        cls,
        operation_def: gql_def.OperationDefinitionNode,
        evaluator: SchemaEvaluator,
        directives: list[str],
        variables: list[QtGqlVariableDefinition],
    ):
        return cls(
            operation_def=operation_def,
            evaluator=evaluator,
            directives=directives,
            variables=variables,
        )
