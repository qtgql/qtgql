import QtQuick
import QtQuick.Layouts
import GraphQL.QmlUsage.FriendsListQuery
Window {
    visible:true;
    Item {
        id: root
        objectName: "root"
        property var model: undefined

        Rectangle {
            anchors.fill: parent
            Text {
                text: `model is: ${root.model}`
            }
            color: "red"
            ListView {
                anchors.fill: parent
                objectName: "friendsList"
                model: root.model?.data?.friends
                delegate: Rectangle {
                    width: root.width
                    height: 100

                    Text {
                        property Friend__friends friend: model.data
                        text: `name: ${friend?.name} age: ${friend?.age}`
                    }
                }
            }
        }
    }
}
