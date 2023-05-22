#include <QObject>

class FooQObject : public QObject {
  Q_OBJECT
 public:
  QString val = "foo";

  FooQObject(const QString& _foo) : val(_foo), QObject(nullptr) {}
};
