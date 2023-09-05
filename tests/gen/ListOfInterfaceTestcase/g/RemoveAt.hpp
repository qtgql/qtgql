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

namespace ListOfInterfaceTestcase::removeat {
class RemoveAt;

namespace deserializers {
std::shared_ptr<Cat> des_Cat__removeAtpets(const QJsonObject &data,
                                           const RemoveAt *operation);
std::shared_ptr<Dog> des_Dog__removeAtpets(const QJsonObject &data,
                                           const RemoveAt *operation);
std::shared_ptr<Person> des_Person__removeAt(const QJsonObject &data,
                                             const RemoveAt *operation);
std::shared_ptr<Pet> des_Pet__removeAtpets(const QJsonObject &data,
                                           const RemoveAt *operation);
}; // namespace deserializers

namespace updaters {
void update_Cat__removeAtpets(const std::shared_ptr<Cat> &inst,
                              const QJsonObject &data,
                              const RemoveAt *operation);
void update_Dog__removeAtpets(const std::shared_ptr<Dog> &inst,
                              const QJsonObject &data,
                              const RemoveAt *operation);
void update_Person__removeAt(const std::shared_ptr<Person> &inst,
                             const QJsonObject &data,
                             const RemoveAt *operation);
void update_Mutation__(const std::shared_ptr<Mutation> &inst,
                       const QJsonObject &data, const RemoveAt *operation);
}; // namespace updaters

// ------------ Forward declarations ------------
class Cat__removeAtpets;
class Dog__removeAtpets;
class Person__removeAt;

// ------------ Narrowed Interfaces ------------
class QTGQL_EXPORT_FOR_UNIT_TESTS Pet__removeAtpets
    : public qtgql::bases::ObjectTypeABC {

  Q_OBJECT
  QML_ELEMENT
  QML_UNCREATABLE("QtGql does not supports instantiation via qml")
  Q_PROPERTY(QString __typeName READ __typename CONSTANT)

  Q_PROPERTY(const QString &name READ get_name NOTIFY nameChanged);

signals:
  void nameChanged();

protected:
  std::shared_ptr<ListOfInterfaceTestcase::Pet> m_inst;

public:
  using qtgql::bases::ObjectTypeABC::ObjectTypeABC;
  [[nodiscard]] inline virtual const QString &get_name() const {
    throw qtgql::exceptions::InterfaceDirectAccessError("Pet");
  }
};

// ------------ Narrowed Object types ------------

class QTGQL_EXPORT_FOR_UNIT_TESTS Cat__removeAtpets : public Pet__removeAtpets {

  RemoveAt *m_operation;

  Q_OBJECT
  QML_ELEMENT
  QML_UNCREATABLE("QtGql does not supports instantiation via qml")
  Q_PROPERTY(QString __typeName READ __typename CONSTANT)

  Q_PROPERTY(const QString &name READ get_name NOTIFY nameChanged);
  Q_PROPERTY(const QString &color READ get_color NOTIFY colorChanged);

signals:
  void nameChanged();
  void colorChanged();

protected:
  std::shared_ptr<ListOfInterfaceTestcase::Cat> m_inst;

public:
  // args builders

  Cat__removeAtpets(RemoveAt *operation, const std::shared_ptr<Cat> &inst);
  void qtgql_replace_concrete(const std::shared_ptr<Cat> &new_inst);

protected:
  void _qtgql_connect_signals();

public:
  [[nodiscard]] const QString &get_name() const;
  [[nodiscard]] const QString &get_color() const;

public:
  [[nodiscard]] const QString &__typename() const final {
    return m_inst->__typename();
  }
};

class QTGQL_EXPORT_FOR_UNIT_TESTS Dog__removeAtpets : public Pet__removeAtpets {

  RemoveAt *m_operation;

  Q_OBJECT
  QML_ELEMENT
  QML_UNCREATABLE("QtGql does not supports instantiation via qml")
  Q_PROPERTY(QString __typeName READ __typename CONSTANT)

  Q_PROPERTY(const QString &name READ get_name NOTIFY nameChanged);
  Q_PROPERTY(const int &age READ get_age NOTIFY ageChanged);

signals:
  void nameChanged();
  void ageChanged();

protected:
  std::shared_ptr<ListOfInterfaceTestcase::Dog> m_inst;

public:
  // args builders

  Dog__removeAtpets(RemoveAt *operation, const std::shared_ptr<Dog> &inst);
  void qtgql_replace_concrete(const std::shared_ptr<Dog> &new_inst);

protected:
  void _qtgql_connect_signals();

public:
  [[nodiscard]] const QString &get_name() const;
  [[nodiscard]] const int &get_age() const;

public:
  [[nodiscard]] const QString &__typename() const final {
    return m_inst->__typename();
  }
};

class QTGQL_EXPORT_FOR_UNIT_TESTS Person__removeAt
    : public qtgql::bases::ObjectTypeABC {

  RemoveAt *m_operation;

  Q_OBJECT
  QML_ELEMENT
  QML_UNCREATABLE("QtGql does not supports instantiation via qml")
  Q_PROPERTY(QString __typeName READ __typename CONSTANT)

  Q_PROPERTY(const QString &name READ get_name NOTIFY nameChanged);
  Q_PROPERTY(const qtgql::bases::ListModelABC<Pet__removeAtpets *> *pets READ
                 get_pets NOTIFY petsChanged);
  Q_PROPERTY(const qtgql::bases::scalars::Id &id READ get_id NOTIFY idChanged);

signals:
  void nameChanged();
  void petsChanged();
  void idChanged();

protected:
  std::shared_ptr<ListOfInterfaceTestcase::Person> m_inst;
  qtgql::bases::ListModelABC<Pet__removeAtpets *> *m_pets;

public:
  // args builders

  Person__removeAt(RemoveAt *operation, const std::shared_ptr<Person> &inst);
  void qtgql_replace_concrete(const std::shared_ptr<Person> &new_inst);

protected:
  void _qtgql_connect_signals();

public:
  [[nodiscard]] const QString &get_name() const;
  [[nodiscard]] const qtgql::bases::ListModelABC<Pet__removeAtpets *> *
  get_pets() const;
  [[nodiscard]] const qtgql::bases::scalars::Id &get_id() const;

public:
  [[nodiscard]] const QString &__typename() const final {
    return m_inst->__typename();
  }
};

class QTGQL_EXPORT_FOR_UNIT_TESTS Mutation__
    : public qtgql::bases::ObjectTypeABC {

  RemoveAt *m_operation;

  Q_OBJECT
  QML_ELEMENT
  QML_UNCREATABLE("QtGql does not supports instantiation via qml")
  Q_PROPERTY(QString __typeName READ __typename CONSTANT)

  Q_PROPERTY(const Person__removeAt *removeAt READ get_removeAt NOTIFY
                 removeAtChanged);

signals:
  void removeAtChanged();

protected:
  std::shared_ptr<ListOfInterfaceTestcase::Mutation> m_inst;
  Person__removeAt *m_removeAt = {};

public:
  // args builders
  static QJsonObject build_args_for_removeAt(const RemoveAt *operation);

  Mutation__(RemoveAt *operation, const std::shared_ptr<Mutation> &inst);

protected:
  void _qtgql_connect_signals();

public:
  [[nodiscard]] const Person__removeAt *get_removeAt() const;

public:
  [[nodiscard]] const QString &__typename() const final {
    return m_inst->__typename();
  }
};

struct RemoveAtVariables {
  qtgql::bases::scalars::Id nodeId;
  int at;
  QJsonObject to_json() const {
    QJsonObject __ret;

    __ret.insert("nodeId", nodeId);

    __ret.insert("at", at);

    return __ret;
  }
};

class QTGQL_EXPORT_FOR_UNIT_TESTS RemoveAt
    : public qtgql::bases::OperationHandlerABC {
  Q_OBJECT
  Q_PROPERTY(const Mutation__ *data READ data NOTIFY dataChanged);
  QML_ELEMENT
  QML_UNCREATABLE("Must be instantiated as shared pointer.")

  std::optional<Mutation__ *> m_data = std::nullopt;

  inline const QString &ENV_NAME() final {
    static const auto ret = QString("ListOfInterfaceTestcase");
    return ret;
  }
signals:
  void dataChanged();

public:
  RemoveAtVariables vars_inst;

  RemoveAt()
      : qtgql::bases::OperationHandlerABC(qtgql::bases::GraphQLMessage(
            "mutation RemoveAt($nodeId: ID!, $at: Int!) {"
            "  removeAt(nodeId: $nodeId, at: $at) {"
            "    name"
            "    pets {"
            "      name"
            "      ... on Dog {"
            "        name"
            "        age"
            "      }"
            "      ... on Cat {"
            "        name"
            "        color"
            "      }"
            "      __typename"
            "    }"
            "    id"
            "  }"
            "}")){};

  QTGQL_STATIC_MAKE_SHARED(RemoveAt)

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

  void set_variables(RemoveAtVariables vars) {

    vars_inst.nodeId = vars.nodeId;

    vars_inst.at = vars.at;
    qtgql::bases::OperationHandlerABC::set_vars(vars_inst.to_json());
  }
};

class UseRemoveAt : public QObject {
  Q_OBJECT
  QML_ELEMENT
  Q_PROPERTY(const Mutation__ *data READ data NOTIFY dataChanged);
  Q_PROPERTY(bool completed READ completed NOTIFY completedChanged)
  Q_PROPERTY(bool operationOnFlight READ operation_on_flight NOTIFY
                 operationOnFlightChanged)

public:
  std::shared_ptr<RemoveAt> m_operation;

  UseRemoveAt(QObject *parent = nullptr) : QObject(parent) {
    m_operation = RemoveAt::shared();
    auto op_ptr = m_operation.get();
    connect(op_ptr, &RemoveAt::dataChanged, this, [&] { emit dataChanged(); });
    connect(op_ptr, &RemoveAt::completedChanged, this,
            [&] { emit completedChanged(); });
    connect(op_ptr, &RemoveAt::operationOnFlightChanged, this,
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
}; // namespace ListOfInterfaceTestcase::removeat
