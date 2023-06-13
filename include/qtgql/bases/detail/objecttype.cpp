#include "objecttype.hpp"

namespace qtgql {
    namespace bases{




        void NodeInstanceStore::add_node(const std::shared_ptr <NodeInterfaceABC> &node) {
            if (node.get()) {
                m_records.emplace(node->get_id(), node);
            }
        }

        std::optional <std::shared_ptr<NodeInterfaceABC>> NodeInstanceStore::get_node(const QString &id) const {
            if (m_records.contains(id)) {
                return {m_records.at(id)};
            }
            return {};
        }

        NodeInstanceStore &NodeInterfaceABC::NODE_STORE() {
            static auto _store = bases::NodeInstanceStore();
            return _store;
        }

    }
}
