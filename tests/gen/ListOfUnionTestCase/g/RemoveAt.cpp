#include "./RemoveAt.hpp"

namespace ListOfUnionTestCase::removeat {

// Interfaces

// Constructor
Dog__removeAtpets::Dog__removeAtpets(RemoveAt *operation,
                                     const std::shared_ptr<Dog> &inst)
    : m_inst{inst}, ObjectTypeABC ::ObjectTypeABC(operation) {
  m_operation = operation;

  _qtgql_connect_signals();
}

void Dog__removeAtpets::_qtgql_connect_signals() {
  auto m_inst_ptr = m_inst.get();
  Q_ASSERT_X(m_inst_ptr, __FILE__,
             "Tried to instantiate a proxy object with an empty pointer!");
  connect(m_inst_ptr, &ListOfUnionTestCase::Dog::nameChanged, this, [&]() {
    auto operation = m_operation;
    emit nameChanged();
  });
  connect(m_inst_ptr, &ListOfUnionTestCase::Dog::ageChanged, this, [&]() {
    auto operation = m_operation;
    emit ageChanged();
  });
  connect(m_inst_ptr, &ListOfUnionTestCase::Dog::idChanged, this, [&]() {
    auto operation = m_operation;
    emit idChanged();
  });
};

// Deserialzier

std::shared_ptr<Dog>
deserializers::des_Dog__removeAtpets(const QJsonObject &data,
                                     const RemoveAt *operation) {
  if (data.isEmpty()) {
    return {};
  }

  auto cached_maybe = Dog::get_node(data.value("id").toString());
  if (cached_maybe.has_value()) {
    auto node = cached_maybe.value();
    updaters::update_Dog__removeAtpets(node, data, operation);
    return node;
  }
  auto inst = Dog::shared();

  if (!data.value("name").isNull()) {
    inst->set_name(std::make_shared<QString>(data.value("name").toString()));
  };

  if (!data.value("age").isNull()) {
    inst->set_age(std::make_shared<int>(data.value("age").toInt()));
  };

  if (!data.value("id").isNull()) {
    inst->set_id(std::make_shared<qtgql::bases::scalars::Id>(
        data.value("id").toString()));
  };

  Dog::ENV_CACHE()->add_node(inst);

  return inst;
};

// Updater
void updaters::update_Dog__removeAtpets(const std::shared_ptr<Dog> &inst,
                                        const QJsonObject &data,
                                        const RemoveAt *operation) {
  if (!data.value("name").isNull()) {
    auto new_name = std::make_shared<QString>(data.value("name").toString());
    if (*inst->m_name != *new_name) {
      inst->set_name(new_name);
    }
  }

  if (!data.value("age").isNull()) {
    auto new_age = std::make_shared<int>(data.value("age").toInt());
    if (*inst->m_age != *new_age) {
      inst->set_age(new_age);
    }
  }

  if (!data.value("id").isNull()) {
    auto new_id = std::make_shared<qtgql::bases::scalars::Id>(
        data.value("id").toString());
    if (*inst->m_id != *new_id) {
      inst->set_id(new_id);
    }
  }
};

// Dog__removeAtpets Getters
[[nodiscard]] const QString &Dog__removeAtpets::get_name() const {
  return *m_inst->get_name();
  ;
};
[[nodiscard]] const int &Dog__removeAtpets::get_age() const {
  return *m_inst->get_age();
  ;
};
[[nodiscard]] const qtgql::bases::scalars::Id &
Dog__removeAtpets::get_id() const {
  return *m_inst->get_id();
  ;
};

// args builders

void Dog__removeAtpets::qtgql_replace_concrete(
    const std::shared_ptr<Dog> &new_inst) {
  if (new_inst == m_inst) {
    return;
  }
  m_inst->disconnect(this);
  if (m_inst->m_name != new_inst->m_name) {

    auto operation = m_operation;
    emit nameChanged();
  };
  if (m_inst->m_age != new_inst->m_age) {

    auto operation = m_operation;
    emit ageChanged();
  };
  if (m_inst->m_id != new_inst->m_id) {

    auto operation = m_operation;
    emit idChanged();
  };
  m_inst = new_inst;
  _qtgql_connect_signals();
};
// Constructor
Cat__removeAtpets::Cat__removeAtpets(RemoveAt *operation,
                                     const std::shared_ptr<Cat> &inst)
    : m_inst{inst}, ObjectTypeABC ::ObjectTypeABC(operation) {
  m_operation = operation;

  _qtgql_connect_signals();
}

void Cat__removeAtpets::_qtgql_connect_signals() {
  auto m_inst_ptr = m_inst.get();
  Q_ASSERT_X(m_inst_ptr, __FILE__,
             "Tried to instantiate a proxy object with an empty pointer!");
  connect(m_inst_ptr, &ListOfUnionTestCase::Cat::nameChanged, this, [&]() {
    auto operation = m_operation;
    emit nameChanged();
  });
  connect(m_inst_ptr, &ListOfUnionTestCase::Cat::colorChanged, this, [&]() {
    auto operation = m_operation;
    emit colorChanged();
  });
};

// Deserialzier

std::shared_ptr<Cat>
deserializers::des_Cat__removeAtpets(const QJsonObject &data,
                                     const RemoveAt *operation) {
  if (data.isEmpty()) {
    return {};
  }
  auto inst = Cat::shared();

  if (!data.value("name").isNull()) {
    inst->set_name(std::make_shared<QString>(data.value("name").toString()));
  };

  if (!data.value("color").isNull()) {
    inst->set_color(std::make_shared<QString>(data.value("color").toString()));
  };

  return inst;
};

// Updater
void updaters::update_Cat__removeAtpets(const std::shared_ptr<Cat> &inst,
                                        const QJsonObject &data,
                                        const RemoveAt *operation) {
  if (!data.value("name").isNull()) {
    auto new_name = std::make_shared<QString>(data.value("name").toString());
    if (*inst->m_name != *new_name) {
      inst->set_name(new_name);
    }
  }

  if (!data.value("color").isNull()) {
    auto new_color = std::make_shared<QString>(data.value("color").toString());
    if (*inst->m_color != *new_color) {
      inst->set_color(new_color);
    }
  }
};

// Cat__removeAtpets Getters
[[nodiscard]] const QString &Cat__removeAtpets::get_name() const {
  return *m_inst->get_name();
  ;
};
[[nodiscard]] const QString &Cat__removeAtpets::get_color() const {
  return *m_inst->get_color();
  ;
};

// args builders

void Cat__removeAtpets::qtgql_replace_concrete(
    const std::shared_ptr<Cat> &new_inst) {
  if (new_inst == m_inst) {
    return;
  }
  m_inst->disconnect(this);
  if (m_inst->m_name != new_inst->m_name) {

    auto operation = m_operation;
    emit nameChanged();
  };
  if (m_inst->m_color != new_inst->m_color) {

    auto operation = m_operation;
    emit colorChanged();
  };
  m_inst = new_inst;
  _qtgql_connect_signals();
};
// Constructor
Person__removeAt::Person__removeAt(RemoveAt *operation,
                                   const std::shared_ptr<Person> &inst)
    : m_inst{inst}, ObjectTypeABC ::ObjectTypeABC(operation) {
  m_operation = operation;

  auto init_vec_pets = std::vector<qtgql::bases::ObjectTypeABC *>();
  for (const auto &node : m_inst->get_pets()) {
    auto pets_typename = node->__typename();
    if (pets_typename == "Dog") {
      init_vec_pets.push_back(
          qobject_cast<qtgql::bases::ObjectTypeABC *>(new Dog__removeAtpets(
              operation, std::static_pointer_cast<Dog>(node))));

    }

    else if (pets_typename == "Cat") {
      init_vec_pets.push_back(
          qobject_cast<qtgql::bases::ObjectTypeABC *>(new Cat__removeAtpets(
              operation, std::static_pointer_cast<Cat>(node))));

    } else {
      throw qtgql::exceptions::InterfaceDeserializationError(
          {pets_typename.toStdString()});
    }
  }
  m_pets = new qtgql::bases::ListModelABC<qtgql::bases::ObjectTypeABC *>(
      this, std::move(init_vec_pets));

  _qtgql_connect_signals();
}

void Person__removeAt::_qtgql_connect_signals() {
  auto m_inst_ptr = m_inst.get();
  Q_ASSERT_X(m_inst_ptr, __FILE__,
             "Tried to instantiate a proxy object with an empty pointer!");
  connect(m_inst_ptr, &ListOfUnionTestCase::Person::nameChanged, this, [&]() {
    auto operation = m_operation;
    emit nameChanged();
  });
  connect(m_inst_ptr, &ListOfUnionTestCase::Person::petsChanged, this, [&]() {
    auto operation = m_operation;
    auto new_data = m_inst->get_pets();
    auto new_len = new_data.size();
    auto prev_len = m_pets->rowCount();
    if (new_len < prev_len) {
      m_pets->removeRows(prev_len - 1, prev_len - new_len);
    }
    for (int i = 0; i < new_len; i++) {
      const auto &concrete = new_data.at(i);

      auto pets_typename = concrete->__typename();

      if (pets_typename == "Dog") {
        if (i >= prev_len) {
          m_pets->append(new Dog__removeAtpets(
              operation, std::static_pointer_cast<Dog>(concrete)));
        } else {
          auto proxy_to_update = m_pets->get(i);
          if (proxy_to_update && proxy_to_update->__typename() == "Dog") {
            qobject_cast<Dog__removeAtpets *>(proxy_to_update)
                ->qtgql_replace_concrete(
                    std::static_pointer_cast<Dog>(concrete));
          } else {
            m_pets->replace(
                i, new Dog__removeAtpets(
                       operation, std::static_pointer_cast<Dog>(concrete)));
            delete proxy_to_update;
          }
        }

      }

      else if (pets_typename == "Cat") {
        if (i >= prev_len) {
          m_pets->append(new Cat__removeAtpets(
              operation, std::static_pointer_cast<Cat>(concrete)));
        } else {
          auto proxy_to_update = m_pets->get(i);
          if (proxy_to_update && proxy_to_update->__typename() == "Cat") {
            qobject_cast<Cat__removeAtpets *>(proxy_to_update)
                ->qtgql_replace_concrete(
                    std::static_pointer_cast<Cat>(concrete));
          } else {
            m_pets->replace(
                i, new Cat__removeAtpets(
                       operation, std::static_pointer_cast<Cat>(concrete)));
            delete proxy_to_update;
          }
        }

      } else {
        throw qtgql::exceptions::InterfaceDeserializationError(
            {pets_typename.toStdString()});
      }
    }
  });
  connect(m_inst_ptr, &ListOfUnionTestCase::Person::idChanged, this, [&]() {
    auto operation = m_operation;
    emit idChanged();
  });
};

// Deserialzier

std::shared_ptr<Person>
deserializers::des_Person__removeAt(const QJsonObject &data,
                                    const RemoveAt *operation) {
  if (data.isEmpty()) {
    return {};
  }

  auto cached_maybe = Person::get_node(data.value("id").toString());
  if (cached_maybe.has_value()) {
    auto node = cached_maybe.value();
    updaters::update_Person__removeAt(node, data, operation);
    return node;
  }
  auto inst = Person::shared();

  if (!data.value("name").isNull()) {
    inst->set_name(std::make_shared<QString>(data.value("name").toString()));
  };

  if (!data.value("pets").isNull()) {

    std::vector<std::shared_ptr<qtgql::bases::ObjectTypeABC>> pets_init_vec;
    for (const auto &node : data.value("pets").toArray()) {

      auto node_data = node.toObject();
      auto pets_typename = node_data.value("__typename").toString();
      if (pets_typename == "Dog") {
        pets_init_vec.push_back(
            deserializers::des_Dog__removeAtpets(node_data, operation));

      }

      else if (pets_typename == "Cat") {
        pets_init_vec.push_back(
            deserializers::des_Cat__removeAtpets(node_data, operation));

      } else {
        throw qtgql::exceptions::InterfaceDeserializationError(
            {pets_typename.toStdString()});
      }
    };
    inst->set_pets(pets_init_vec);
  };

  if (!data.value("id").isNull()) {
    inst->set_id(std::make_shared<qtgql::bases::scalars::Id>(
        data.value("id").toString()));
  };

  Person::ENV_CACHE()->add_node(inst);

  return inst;
};

// Updater
void updaters::update_Person__removeAt(const std::shared_ptr<Person> &inst,
                                       const QJsonObject &data,
                                       const RemoveAt *operation) {
  if (!data.value("name").isNull()) {
    auto new_name = std::make_shared<QString>(data.value("name").toString());
    if (*inst->m_name != *new_name) {
      inst->set_name(new_name);
    }
  }

  if (!data.value("pets").isNull()) {

    if (!data.value("pets").isNull()) {

      std::vector<std::shared_ptr<qtgql::bases::ObjectTypeABC>> pets_init_vec;
      for (const auto &node : data.value("pets").toArray()) {

        auto node_data = node.toObject();
        auto pets_typename = node_data.value("__typename").toString();
        if (pets_typename == "Dog") {
          pets_init_vec.push_back(
              deserializers::des_Dog__removeAtpets(node_data, operation));

        }

        else if (pets_typename == "Cat") {
          pets_init_vec.push_back(
              deserializers::des_Cat__removeAtpets(node_data, operation));

        } else {
          throw qtgql::exceptions::InterfaceDeserializationError(
              {pets_typename.toStdString()});
        }
      };
      inst->set_pets(pets_init_vec);
    };
  }

  if (!data.value("id").isNull()) {
    auto new_id = std::make_shared<qtgql::bases::scalars::Id>(
        data.value("id").toString());
    if (*inst->m_id != *new_id) {
      inst->set_id(new_id);
    }
  }
};

// Person__removeAt Getters
[[nodiscard]] const QString &Person__removeAt::get_name() const {
  return *m_inst->get_name();
  ;
};
[[nodiscard]] const qtgql::bases::ListModelABC<qtgql::bases::ObjectTypeABC *> *
Person__removeAt::get_pets() const {
  return m_pets;
};
[[nodiscard]] const qtgql::bases::scalars::Id &
Person__removeAt::get_id() const {
  return *m_inst->get_id();
  ;
};

// args builders

void Person__removeAt::qtgql_replace_concrete(
    const std::shared_ptr<Person> &new_inst) {
  if (new_inst == m_inst) {
    return;
  }
  m_inst->disconnect(this);
  if (m_inst->m_name != new_inst->m_name) {

    auto operation = m_operation;
    emit nameChanged();
  };
  if (m_inst->m_pets != new_inst->m_pets) {

    auto operation = m_operation;
    auto new_data = m_inst->get_pets();
    auto new_len = new_data.size();
    auto prev_len = m_pets->rowCount();
    if (new_len < prev_len) {
      m_pets->removeRows(prev_len - 1, prev_len - new_len);
    }
    for (int i = 0; i < new_len; i++) {
      const auto &concrete = new_data.at(i);

      auto pets_typename = concrete->__typename();

      if (pets_typename == "Dog") {
        if (i >= prev_len) {
          m_pets->append(new Dog__removeAtpets(
              operation, std::static_pointer_cast<Dog>(concrete)));
        } else {
          auto proxy_to_update = m_pets->get(i);
          if (proxy_to_update && proxy_to_update->__typename() == "Dog") {
            qobject_cast<Dog__removeAtpets *>(proxy_to_update)
                ->qtgql_replace_concrete(
                    std::static_pointer_cast<Dog>(concrete));
          } else {
            m_pets->replace(
                i, new Dog__removeAtpets(
                       operation, std::static_pointer_cast<Dog>(concrete)));
            delete proxy_to_update;
          }
        }

      }

      else if (pets_typename == "Cat") {
        if (i >= prev_len) {
          m_pets->append(new Cat__removeAtpets(
              operation, std::static_pointer_cast<Cat>(concrete)));
        } else {
          auto proxy_to_update = m_pets->get(i);
          if (proxy_to_update && proxy_to_update->__typename() == "Cat") {
            qobject_cast<Cat__removeAtpets *>(proxy_to_update)
                ->qtgql_replace_concrete(
                    std::static_pointer_cast<Cat>(concrete));
          } else {
            m_pets->replace(
                i, new Cat__removeAtpets(
                       operation, std::static_pointer_cast<Cat>(concrete)));
            delete proxy_to_update;
          }
        }

      } else {
        throw qtgql::exceptions::InterfaceDeserializationError(
            {pets_typename.toStdString()});
      }
    }
  };
  if (m_inst->m_id != new_inst->m_id) {

    auto operation = m_operation;
    emit idChanged();
  };
  m_inst = new_inst;
  _qtgql_connect_signals();
};
// Constructor
Mutation__::Mutation__(RemoveAt *operation,
                       const std::shared_ptr<Mutation> &inst)
    : m_inst{inst}, ObjectTypeABC ::ObjectTypeABC(operation) {
  m_operation = operation;
  auto args_for_removeAt = Mutation__::build_args_for_removeAt(operation);

  m_removeAt =
      new Person__removeAt(operation, m_inst->get_removeAt(args_for_removeAt));

  _qtgql_connect_signals();
}

void Mutation__::_qtgql_connect_signals() {
  auto m_inst_ptr = m_inst.get();
  Q_ASSERT_X(m_inst_ptr, __FILE__,
             "Tried to instantiate a proxy object with an empty pointer!");
  connect(m_inst_ptr, &ListOfUnionTestCase::Mutation::removeAtChanged, this,
          [&]() {
            auto args_for_removeAt =
                Mutation__::build_args_for_removeAt(m_operation);

            auto operation = m_operation;
            auto concrete = m_inst->get_removeAt(args_for_removeAt);
            if (m_removeAt) {
              m_removeAt->qtgql_replace_concrete(concrete);
            } else {
              m_removeAt = new Person__removeAt(operation, concrete);
              emit removeAtChanged();
            }
          });
};

// Deserialzier

// Updater
void updaters::update_Mutation__(const std::shared_ptr<Mutation> &inst,
                                 const QJsonObject &data,
                                 const RemoveAt *operation) {
  QJsonObject m_removeAt_args = Mutation__::build_args_for_removeAt(operation);
  if (!qtgql::bases::backports::map_contains(inst->m_removeAt, m_removeAt_args))

  {
    if (!data.value("removeAt").isNull()) {
      inst->set_removeAt(deserializers::des_Person__removeAt(
                             data.value("removeAt").toObject(), operation),
                         Mutation__::build_args_for_removeAt(operation));
    };
  } else if (!data.value("removeAt").isNull()) {

    auto removeAt_data = data.value("removeAt").toObject();

    if (inst->m_removeAt.at(m_removeAt_args) &&
        *inst->m_removeAt.at(m_removeAt_args)->get_id() ==
            removeAt_data.value("id").toString()) {
      updaters::update_Person__removeAt(inst->m_removeAt.at(m_removeAt_args),
                                        removeAt_data, operation);
    } else {
      inst->set_removeAt(
          deserializers::des_Person__removeAt(removeAt_data, operation),
          m_removeAt_args);
    }
  }
};

// Mutation__ Getters
[[nodiscard]] const Person__removeAt *Mutation__::get_removeAt() const {
  return m_removeAt;
};

// args builders
QJsonObject Mutation__::build_args_for_removeAt(const RemoveAt *operation) {
  QJsonObject qtgql__ret;

  qtgql__ret.insert("nodeId", operation->vars_inst.nodeId);

  qtgql__ret.insert("at", operation->vars_inst.at);

  return qtgql__ret;
}

} // namespace ListOfUnionTestCase::removeat
