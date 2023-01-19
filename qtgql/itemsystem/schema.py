from typing import Optional, Type, TypeVar, Union, get_type_hints
from uuid import UUID

import attrs
from PySide6.QtCore import Qt

from qtgql.itemsystem.model import GenericModel, NodeHelper, NodeProto, Role, RoleMapper
from qtgql.itemsystem.type_ import IS_ROLE, BaseType, field_is

T = TypeVar("T")


class Schema:
    __slots__ = ("query", "mutation", "subscription", "_types", "_deferred_types", "nodes", "types")

    def __init__(
        self,
        *,
        query: Type[BaseType],
        mutation: Optional[Type[BaseType]] = None,
        subscriptions: Optional[Type[BaseType]] = None,
    ):
        self.query = query
        self.mutation = mutation
        self.subscription = subscriptions
        self.nodes: dict[Union[UUID, str], NodeHelper] = {}
        if mutation:
            assert mutation.__types_store__ is query.__types_store__
        if subscriptions:
            assert subscriptions.__types_store__ is query.__types_store__

        self.types = query.__types_store__
        self._evaluate_types()

    def _evaluate_types(self) -> None:
        types = globals().copy()
        types.update(self.types)
        for t in self.types.values():
            roles = RoleMapper()
            tp_hints = get_type_hints(t, globalns=types)
            for role_num, field in enumerate(attrs.fields(t), int(Qt.ItemDataRole.UserRole)):  # type: ignore
                # assign role and check if not exists
                if field_is(IS_ROLE, field):
                    role_ = Role.create(
                        name=field.name, role_num=role_num, type_=tp_hints[field.name]
                    )
                    # fill the role manager
                    roles.by_num[role_num] = role_
                    roles.by_name[role_.name] = role_
                    roles.qt_roles[role_.num] = role_.qt_name
                    # lists must be child models
                    if role_.type.type is GenericModel:
                        child_type = role_.type.of_type[0].type
                        roles.children[role_.name] = child_type

            t.Model = GenericModel.from_role_defined(t)
            t.Model.__roles__ = roles

    def get_node(self, node: NodeProto) -> Optional[NodeHelper[NodeProto]]:
        return self.nodes.get(node.uuid, None)

    def update_node(self, node: NodeProto) -> bool:
        """
        :return: True if update succeeded
        """
        if node_helper := self.get_node(node):
            model = node_helper.model
            node_model_index = model._data.index(node_helper.node)
            # replace old node
            model._data[node_model_index] = node
            self.nodes[node.uuid].node = node
            # notify changes
            index = model.index(node_model_index)
            model.dataChanged.emit(index, index)  # type: ignore
            return True
        return False
