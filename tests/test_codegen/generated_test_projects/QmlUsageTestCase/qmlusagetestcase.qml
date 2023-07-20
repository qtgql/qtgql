import QtQuick
import QtQuick.Layouts
import GraphQL.QmlUsageTestCase.MainQuery

Item {
    id: root
    objectName: "foobar"
    property bool success: false
    UseMainQuery {
        id: main_query

        Component.onCompleted: {
            main_query.fetch();
        }
    }
    Rectangle {
        anchors.fill: parent

        ColumnLayout {
            Text {
                text: `completed ${main_query.completed}`
            }
            ListView {
                model: main_query.data?.user.friends
                delegate: Text {
                    property Person__userfriends friend: model.qtObject
                    text: `name: ${friend.name} age: ${friend.age}`
                    Component.onCompleted: {
                        if (friend.name != "") {
                            root.success = true;
                        }
                        ;
                    }
                }
            }
        }
    }
}
