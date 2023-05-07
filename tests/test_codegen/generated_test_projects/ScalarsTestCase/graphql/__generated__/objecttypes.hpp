
#include <QObject>
#include <graphqlmetadata.hpp>

// ----------------------------------------- Object Types
// -----------------------------------------

class Query : public _BaseQGraphQLObject, {
  static const QString TYPE_NAME = "Query"

      public : Query(QObject* parent = None, user
                     : Optional[Optional[User]] = None, )
      : QObject::QObject(parent) {
    m_user = user if user else None
  };

  void user_setter(const Optional[User] & v){m_user = v emit userChanged()};

 signals:

  void userChanged();

  std::shared_ptr<Query> from_json(QObject* parent, const QJsonObject& data,
                                   const SelectionConfig& config,
                                   const OperationMetaData& metadata) {
    auto inst = std::make_shared<Query>();

    if
      'user' in config.selections.keys()
          :

            field_data = data.get('user', None)

                             inner_config = config
                                                .selections['user']

                                            if field_data : inst.m_user =
          User.from_dict(parent, field_data, inner_config, metadata, )

              return inst
  }
};

class User : public _BaseQGraphQLObjectWithID, Node, {
  static const QString TYPE_NAME = "User"

      public : User(QObject* parent = None, id
                    : Optional[] = None, name
                    : Optional[] = None, age
                    : Optional[] = None, agePoint
                    : Optional[] = None, male
                    : Optional[] = None, uuid
                    : Optional[] = None, )
      : QObject::QObject(parent) {
    m_id = id if id else 9b2a0828 - 880d - 4023 - 9909 - de067984523c m_name =
               name if name else - m_age = age if age else 0 m_agePoint =
                   agePoint if agePoint else 0.0 m_male =
                       male if male else False m_uuid =
                           uuid if uuid else 9b2a0828 - 880d - 4023 - 9909 -
                           de067984523c
  };

  void id_setter(const& v){m_id = v emit idChanged()};

  void name_setter(const& v){m_name = v emit nameChanged()};

  void age_setter(const& v){m_age = v emit ageChanged()};

  void agePoint_setter(const& v){m_agePoint = v emit agePointChanged()};

  void male_setter(const& v){m_male = v emit maleChanged()};

  void uuid_setter(const& v){m_uuid = v emit uuidChanged()};

 signals:

  void idChanged();

  void nameChanged();

  void ageChanged();

  void agePointChanged();

  void maleChanged();

  void uuidChanged();

  std::shared_ptr<User> from_json(QObject* parent, const QJsonObject& data,
                                  const SelectionConfig& config,
                                  const OperationMetaData& metadata) {
    auto inst = std::make_shared<User>();

    if
      'id' in config.selections.keys()
          :

            field_data =
          data.get('id', 9b2a0828 - 880d - 4023 - 9909 - de067984523c)

              inst.m_id = field_data

                          if 'name' in config.selections.keys()
          :

            field_data = data.get('name', -)

                             inst.m_name = field_data

                                           if 'age' in config.selections.keys()
          :

            field_data = data.get('age', 0)

                             inst.m_age =
              field_data

              if 'agePoint' in config.selections.keys()
          :

            field_data = data.get('agePoint', 0.0)

                             inst.m_agePoint =
                  field_data

                  if 'male' in config.selections.keys()
          :

            field_data = data.get('male', False)

                             inst.m_male = field_data

                                           if 'uuid' in config.selections.keys()
          :

            field_data = data.get('uuid',
                                  9b2a0828 - 880d - 4023 - 9909 - de067984523c)

                             inst.m_uuid = field_data

                      record = NodeRecord(node = inst, retainers = set())
                                   .retain(metadata.operation_name)
                                       cls.__store__.add_record(record)

                                           return inst
  }
};
