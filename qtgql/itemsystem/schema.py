import dataclasses
from typing import Optional, Type, TypeVar, Union, get_type_hints
from uuid import UUID

from qtpy.QtCore import Qt

from qtgql.itemsystem.model import GenericModel, NodeHelper, NodeProto
from qtgql.itemsystem.role import (
    IS_ROLE,
    BaseRoleDefined,
    Role,
    RoleMapper,
    TypesStorage,
    field_is,
)

T = TypeVar("T")


class Schema:
    __slots__ = ("query", "mutation", "subscription", "_types", "_deferred_types", "nodes", "types")

    def __init__(
        self,
        *,
        query: Type[BaseRoleDefined],
        types_storage: TypesStorage,
        mutation: Optional[Type[BaseRoleDefined]] = None,
        subscriptions: Optional[Type[BaseRoleDefined]] = None,
    ):
        self.query = query
        self.mutation = mutation
        self.subscription = subscriptions
        self.nodes: dict[Union[UUID, str], NodeHelper] = {}

        self.types = types_storage
        self._evaluate_types()

    def _evaluate_types(self) -> None:
        types = globals().copy()
        types.update(self.types)
        for t in self.types.values():
            roles = RoleMapper()
            tp_hints = get_type_hints(t, globalns=self.types.copy())
            for role_num, field in enumerate(dataclasses.fields(t), int(Qt.ItemDataRole.UserRole)):
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
                    if role_.type.type is list:
                        child_type = role_.type.of_type[0].type
                        roles.children[role_.name] = child_type

            t.__roles__ = roles
            t.Model = GenericModel.from_role_defined(t)

    def get_node(self, node: NodeProto) -> Optional[NodeHelper[T]]:
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
