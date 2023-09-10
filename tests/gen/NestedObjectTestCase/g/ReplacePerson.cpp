#include "./ReplacePerson.hpp"

namespace NestedObjectTestCase::replaceperson {

// Interfaces

// Constructor
Person__replacePersonperson::Person__replacePersonperson(
    ReplacePerson *operation, const std::shared_ptr<Person> &inst)
    : m_inst{inst}, ObjectTypeABC ::ObjectTypeABC(operation) {
  m_operation = operation;

  _qtgql_connect_signals();
}

void Person__replacePersonperson::_qtgql_connect_signals() {
  auto m_inst_ptr = m_inst.get();
  Q_ASSERT_X(m_inst_ptr, __FILE__,
             "Tried to instantiate a proxy object with an empty pointer!");
  connect(m_inst_ptr, &NestedObjectTestCase::Person::nameChanged, this, [&]() {
    auto operation = m_operation;
    emit nameChanged();
  });
  connect(m_inst_ptr, &NestedObjectTestCase::Person::idChanged, this, [&]() {
    auto operation = m_operation;
    emit idChanged();
  });
};

// Deserialzier

std::shared_ptr<Person>
deserializers::des_Person__replacePersonperson(const QJsonObject &data,
                                               const ReplacePerson *operation) {
  if (data.isEmpty()) {
    return {};
  }

  auto cached_maybe = Person::get_node(data.value("id").toString());
  if (cached_maybe.has_value()) {
    auto node = cached_maybe.value();
    updaters::update_Person__replacePersonperson(node, data, operation);
    return node;
  }
  auto inst = Person::shared();

  if (!data.value("name").isNull()) {
    inst->set_name(std::make_shared<QString>(data.value("name").toString()));
  };

  if (!data.value("id").isNull()) {
    inst->set_id(std::make_shared<qtgql::bases::scalars::Id>(
        data.value("id").toString()));
  };

  Person::ENV_CACHE()->add_node(inst);

  return inst;
};

// Updater
void updaters::update_Person__replacePersonperson(
    const std::shared_ptr<Person> &inst, const QJsonObject &data,
    const ReplacePerson *operation) {
  if (!data.value("name").isNull()) {
    auto new_name = std::make_shared<QString>(data.value("name").toString());
    if (*inst->m_name != *new_name) {
      inst->set_name(new_name);
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

// Person__replacePersonperson Getters
[[nodiscard]] const QString &Person__replacePersonperson::get_name() const {
  return *m_inst->get_name();
  ;
};
[[nodiscard]] const qtgql::bases::scalars::Id &
Person__replacePersonperson::get_id() const {
  return *m_inst->get_id();
  ;
};

// args builders

void Person__replacePersonperson::qtgql_replace_concrete(
    const std::shared_ptr<Person> &new_inst) {
  if (new_inst == m_inst) {
    return;
  }
  m_inst->disconnect(this);
  if (m_inst->m_name != new_inst->m_name) {

    auto operation = m_operation;
    emit nameChanged();
  };
  if (m_inst->m_id != new_inst->m_id) {

    auto operation = m_operation;
    emit idChanged();
  };
  m_inst = new_inst;
  _qtgql_connect_signals();
};
// Constructor
User__replacePerson::User__replacePerson(ReplacePerson *operation,
                                         const std::shared_ptr<User> &inst)
    : m_inst{inst}, ObjectTypeABC ::ObjectTypeABC(operation) {
  m_operation = operation;

  m_person = new Person__replacePersonperson(operation, m_inst->get_person());

  _qtgql_connect_signals();
}

void User__replacePerson::_qtgql_connect_signals() {
  auto m_inst_ptr = m_inst.get();
  Q_ASSERT_X(m_inst_ptr, __FILE__,
             "Tried to instantiate a proxy object with an empty pointer!");
  connect(m_inst_ptr, &NestedObjectTestCase::User::personChanged, this, [&]() {
    auto operation = m_operation;
    auto concrete = m_inst->get_person();
    if (m_person) {
      m_person->qtgql_replace_concrete(concrete);
    } else {
      m_person = new Person__replacePersonperson(operation, concrete);
      emit personChanged();
    }
  });
  connect(m_inst_ptr, &NestedObjectTestCase::User::idChanged, this, [&]() {
    auto operation = m_operation;
    emit idChanged();
  });
};

// Deserialzier

std::shared_ptr<User>
deserializers::des_User__replacePerson(const QJsonObject &data,
                                       const ReplacePerson *operation) {
  if (data.isEmpty()) {
    return {};
  }

  auto cached_maybe = User::get_node(data.value("id").toString());
  if (cached_maybe.has_value()) {
    auto node = cached_maybe.value();
    updaters::update_User__replacePerson(node, data, operation);
    return node;
  }
  auto inst = User::shared();

  if (!data.value("person").isNull()) {
    inst->set_person(deserializers::des_Person__replacePersonperson(
        data.value("person").toObject(), operation));
  };

  if (!data.value("id").isNull()) {
    inst->set_id(std::make_shared<qtgql::bases::scalars::Id>(
        data.value("id").toString()));
  };

  User::ENV_CACHE()->add_node(inst);

  return inst;
};

// Updater
void updaters::update_User__replacePerson(const std::shared_ptr<User> &inst,
                                          const QJsonObject &data,
                                          const ReplacePerson *operation) {
  if (!data.value("person").isNull()) {

    auto person_data = data.value("person").toObject();

    if (inst->m_person &&
        *inst->m_person->get_id() == person_data.value("id").toString()) {
      updaters::update_Person__replacePersonperson(inst->m_person, person_data,
                                                   operation);
    } else {
      inst->set_person(deserializers::des_Person__replacePersonperson(
          person_data, operation));
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

// User__replacePerson Getters
[[nodiscard]] const Person__replacePersonperson *
User__replacePerson::get_person() const {
  return m_person;
};
[[nodiscard]] const qtgql::bases::scalars::Id &
User__replacePerson::get_id() const {
  return *m_inst->get_id();
  ;
};

// args builders

void User__replacePerson::qtgql_replace_concrete(
    const std::shared_ptr<User> &new_inst) {
  if (new_inst == m_inst) {
    return;
  }
  m_inst->disconnect(this);
  if (m_inst->m_person != new_inst->m_person) {

    auto operation = m_operation;
    auto concrete = m_inst->get_person();
    if (m_person) {
      m_person->qtgql_replace_concrete(concrete);
    } else {
      m_person = new Person__replacePersonperson(operation, concrete);
      emit personChanged();
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
Mutation__::Mutation__(ReplacePerson *operation,
                       const std::shared_ptr<Mutation> &inst)
    : m_inst{inst}, ObjectTypeABC ::ObjectTypeABC(operation) {
  m_operation = operation;
  auto args_for_replacePerson =
      Mutation__::build_args_for_replacePerson(operation);

  m_replacePerson = new User__replacePerson(
      operation, m_inst->get_replacePerson(args_for_replacePerson));

  _qtgql_connect_signals();
}

void Mutation__::_qtgql_connect_signals() {
  auto m_inst_ptr = m_inst.get();
  Q_ASSERT_X(m_inst_ptr, __FILE__,
             "Tried to instantiate a proxy object with an empty pointer!");
  connect(m_inst_ptr, &NestedObjectTestCase::Mutation::replacePersonChanged,
          this, [&]() {
            auto args_for_replacePerson =
                Mutation__::build_args_for_replacePerson(m_operation);

            auto operation = m_operation;
            auto concrete = m_inst->get_replacePerson(args_for_replacePerson);
            if (m_replacePerson) {
              m_replacePerson->qtgql_replace_concrete(concrete);
            } else {
              m_replacePerson = new User__replacePerson(operation, concrete);
              emit replacePersonChanged();
            }
          });
};

// Deserialzier

// Updater
void updaters::update_Mutation__(const std::shared_ptr<Mutation> &inst,
                                 const QJsonObject &data,
                                 const ReplacePerson *operation) {
  QJsonObject m_replacePerson_args =
      Mutation__::build_args_for_replacePerson(operation);
  if (!qtgql::bases::backports::map_contains(inst->m_replacePerson,
                                             m_replacePerson_args))

  {
    if (!data.value("replacePerson").isNull()) {
      inst->set_replacePerson(
          deserializers::des_User__replacePerson(
              data.value("replacePerson").toObject(), operation),
          Mutation__::build_args_for_replacePerson(operation));
    };
  } else if (!data.value("replacePerson").isNull()) {

    auto replacePerson_data = data.value("replacePerson").toObject();

    if (inst->m_replacePerson.at(m_replacePerson_args) &&
        *inst->m_replacePerson.at(m_replacePerson_args)->get_id() ==
            replacePerson_data.value("id").toString()) {
      updaters::update_User__replacePerson(
          inst->m_replacePerson.at(m_replacePerson_args), replacePerson_data,
          operation);
    } else {
      inst->set_replacePerson(
          deserializers::des_User__replacePerson(replacePerson_data, operation),
          m_replacePerson_args);
    }
  }
};

// Mutation__ Getters
[[nodiscard]] const User__replacePerson *Mutation__::get_replacePerson() const {
  return m_replacePerson;
};

// args builders
QJsonObject
Mutation__::build_args_for_replacePerson(const ReplacePerson *operation) {
  QJsonObject qtgql__ret;

  qtgql__ret.insert("nodeId", operation->vars_inst.nodeId);

  return qtgql__ret;
}

} // namespace NestedObjectTestCase::replaceperson
