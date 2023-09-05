#pragma once
#include "./schema.hpp"
#include <QObject>
#include <QtQml/qqmlregistration.h>
#include <qtgql/bases/bases.hpp>

#if defined(QTGQL_TEST_LIBRARY)
#define QTGQL_EXPORT_FOR_UNIT_TESTS Q_DECL_EXPORT
#else
#define QTGQL_EXPORT_FOR_UNIT_TESTS Q_DECL_IMPORT
#endif

namespace NestedObjectTestCase::replaceperson {
class ReplacePerson;

namespace deserializers {
std::shared_ptr<Person>
des_Person__replacePersonperson(const QJsonObject &data,
                                const ReplacePerson *operation);
std::shared_ptr<User> des_User__replacePerson(const QJsonObject &data,
                                              const ReplacePerson *operation);
}; // namespace deserializers

namespace updaters {
void update_Person__replacePersonperson(const std::shared_ptr<Person> &inst,
                                        const QJsonObject &data,
                                        const ReplacePerson *operation);
void update_User__replacePerson(const std::shared_ptr<User> &inst,
                                const QJsonObject &data,
                                const ReplacePerson *operation);
void update_Mutation__(const std::shared_ptr<Mutation> &inst,
                       const QJsonObject &data, const ReplacePerson *operation);
}; // namespace updaters

// ------------ Forward declarations ------------
class Person__replacePersonperson;
class User__replacePerson;

// ------------ Narrowed Interfaces ------------

// ------------ Narrowed Object types ------------

class QTGQL_EXPORT_FOR_UNIT_TESTS Person__replacePersonperson
    : public qtgql::bases::ObjectTypeABC {

  ReplacePerson *m_operation;

  Q_OBJECT
  QML_ELEMENT
  QML_UNCREATABLE("QtGql does not supports instantiation via qml")
  Q_PROPERTY(QString __typeName READ __typename CONSTANT)

  Q_PROPERTY(const QString &name READ get_name NOTIFY nameChanged);
  Q_PROPERTY(const qtgql::bases::scalars::Id &id READ get_id NOTIFY idChanged);

signals:
  void nameChanged();
  void idChanged();

protected:
  std::shared_ptr<NestedObjectTestCase::Person> m_inst;

public:
  // args builders

  Person__replacePersonperson(ReplacePerson *operation,
                              const std::shared_ptr<Person> &inst);
  void qtgql_replace_concrete(const std::shared_ptr<Person> &new_inst);

protected:
  void _qtgql_connect_signals();

public:
  [[nodiscard]] const QString &get_name() const;
  [[nodiscard]] const qtgql::bases::scalars::Id &get_id() const;

public:
  [[nodiscard]] const QString &__typename() const final {
    return m_inst->__typename();
  }
};

class QTGQL_EXPORT_FOR_UNIT_TESTS User__replacePerson
    : public qtgql::bases::ObjectTypeABC {

  ReplacePerson *m_operation;

  Q_OBJECT
  QML_ELEMENT
  QML_UNCREATABLE("QtGql does not supports instantiation via qml")
  Q_PROPERTY(QString __typeName READ __typename CONSTANT)

  Q_PROPERTY(const Person__replacePersonperson *person READ get_person NOTIFY
                 personChanged);
  Q_PROPERTY(const qtgql::bases::scalars::Id &id READ get_id NOTIFY idChanged);

signals:
  void personChanged();
  void idChanged();

protected:
  std::shared_ptr<NestedObjectTestCase::User> m_inst;
  Person__replacePersonperson *m_person = {};

public:
  // args builders

  User__replacePerson(ReplacePerson *operation,
                      const std::shared_ptr<User> &inst);
  void qtgql_replace_concrete(const std::shared_ptr<User> &new_inst);

protected:
  void _qtgql_connect_signals();

public:
  [[nodiscard]] const Person__replacePersonperson *get_person() const;
  [[nodiscard]] const qtgql::bases::scalars::Id &get_id() const;

public:
  [[nodiscard]] const QString &__typename() const final {
    return m_inst->__typename();
  }
};

class QTGQL_EXPORT_FOR_UNIT_TESTS Mutation__
    : public qtgql::bases::ObjectTypeABC {

  ReplacePerson *m_operation;

  Q_OBJECT
  QML_ELEMENT
  QML_UNCREATABLE("QtGql does not supports instantiation via qml")
  Q_PROPERTY(QString __typeName READ __typename CONSTANT)

  Q_PROPERTY(const User__replacePerson *replacePerson READ get_replacePerson
                 NOTIFY replacePersonChanged);

signals:
  void replacePersonChanged();

protected:
  std::shared_ptr<NestedObjectTestCase::Mutation> m_inst;
  User__replacePerson *m_replacePerson = {};

public:
  // args builders
  static QJsonObject
  build_args_for_replacePerson(const ReplacePerson *operation);

  Mutation__(ReplacePerson *operation, const std::shared_ptr<Mutation> &inst);

protected:
  void _qtgql_connect_signals();

public:
  [[nodiscard]] const User__replacePerson *get_replacePerson() const;

public:
  [[nodiscard]] const QString &__typename() const final {
    return m_inst->__typename();
  }
};

struct ReplacePersonVariables {
  qtgql::bases::scalars::Id nodeId;
  QJsonObject to_json() const {
    QJsonObject __ret;

    __ret.insert("nodeId", nodeId);

    return __ret;
  }
};

class QTGQL_EXPORT_FOR_UNIT_TESTS ReplacePerson
    : public qtgql::bases::OperationHandlerABC {
  Q_OBJECT
  Q_PROPERTY(const Mutation__ *data READ data NOTIFY dataChanged);
  QML_ELEMENT
  QML_UNCREATABLE("Must be instantiated as shared pointer.")

  std::optional<Mutation__ *> m_data = std::nullopt;

  inline const QString &ENV_NAME() final {
    static const auto ret = QString("NestedObjectTestCase");
    return ret;
  }
signals:
  void dataChanged();

public:
  ReplacePersonVariables vars_inst;

  ReplacePerson()
      : qtgql::bases::OperationHandlerABC(qtgql::bases::GraphQLMessage(
            "mutation ReplacePerson($nodeId: ID!) {"
            "  replacePerson(nodeId: $nodeId) {"
            "    person {"
            "      name"
            "      id"
            "    }"
            "    id"
            "  }"
            "}")){};

  QTGQL_STATIC_MAKE_SHARED(ReplacePerson)

  void on_next(const QJsonObject &data_) override {
    auto root_instance = Mutation::instance();
    if (!m_data) {
      updaters::update_Mutation__(root_instance, data_, this);
      m_data = new Mutation__(this, root_instance);
      emit dataChanged();
    } else {
      updaters::update_Mutation__(root_instance, data_, this);
    }
  }

  inline const Mutation__ *data() const {
    if (m_data) {
      return m_data.value();
    }
    return nullptr;
  }

  void set_variables(ReplacePersonVariables vars) {

    vars_inst.nodeId = vars.nodeId;
    qtgql::bases::OperationHandlerABC::set_vars(vars_inst.to_json());
  }
};

class UseReplacePerson : public QObject {
  Q_OBJECT
  QML_ELEMENT
  Q_PROPERTY(const Mutation__ *data READ data NOTIFY dataChanged);
  Q_PROPERTY(bool completed READ completed NOTIFY completedChanged)
  Q_PROPERTY(bool operationOnFlight READ operation_on_flight NOTIFY
                 operationOnFlightChanged)

public:
  std::shared_ptr<ReplacePerson> m_operation;

  UseReplacePerson(QObject *parent = nullptr) : QObject(parent) {
    m_operation = ReplacePerson::shared();
    auto op_ptr = m_operation.get();
    connect(op_ptr, &ReplacePerson::dataChanged, this,
            [&] { emit dataChanged(); });
    connect(op_ptr, &ReplacePerson::completedChanged, this,
            [&] { emit completedChanged(); });
    connect(op_ptr, &ReplacePerson::operationOnFlightChanged, this,
            [&] { emit operationOnFlightChanged(); });
  };

  inline const Mutation__ *data() const { return m_operation->data(); }
  inline bool completed() const { return m_operation->completed(); }
  inline bool operation_on_flight() const {
    return m_operation->operation_on_flight();
  }

public slots:
  void fetch() { m_operation->fetch(); };
  void refetch() { m_operation->refetch(); };

signals:
  void dataChanged();
  void completedChanged();
  void operationOnFlightChanged();
};
}; // namespace NestedObjectTestCase::replaceperson
