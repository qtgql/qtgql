import QtQuick
import GraphQL.QmlUsage.SimpleQuery

Item {
    id: root
    objectName: "root"
    property bool success: false
    UseSimpleQuery {
        id: main_query
        objectName: "useSimpleQuery"
        onCompletedChanged: root.success = true
    }
    Component.onCompleted: {
        main_query.execute();
    }
    Text {
        text: `completed ${main_query.completed}`
    }
}
