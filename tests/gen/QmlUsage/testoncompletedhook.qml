import QtQuick
import GraphQL.QmlUsage.SimpleQuery

Item {
    id: root
    objectName: "root"
    property bool success: false
    UseSimpleQuery {objectName: "useSimpleQuery";
        id: main_query
        onCompletedChanged: root.success = true
    }
    Component.onCompleted: {
        main_query.fetch();
    }
    Text {
        text: `completed ${main_query.completed}`
    }
}
