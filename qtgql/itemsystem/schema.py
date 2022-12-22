from typing import Optional, Type, TypeVar, Union
from uuid import UUID

from qtgql.itemsystem import GenericModel
from qtgql.itemsystem.model import NodeProto, NodeHelper
from qtgql.itemsystem.role import BaseRoleDefined, TypesStorage

T = TypeVar('T')


class Schema:
    __slots__ = ('query', 'mutation', 'subscription', '_types', '_deferred_types', 'nodes', 'types')

    def __init__(self,
                 *,
                 query: Type[BaseRoleDefined],
                 mutation: Optional[Type[BaseRoleDefined]] = None,
                 subscriptions: Optional[Type[BaseRoleDefined]] = None
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

    # def _evaluate_forward_refs(self) -> None:
    #     def evaluate_recursive(t: Type[BaseRoleDefined]) -> None:
    #         for role in t.__roles__.children.values():
    #             if role.
    #     for type_ in self.types.values():

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
