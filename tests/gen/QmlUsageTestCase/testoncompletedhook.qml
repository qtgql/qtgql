import QtQuick
import QtQuick.Layouts
import GraphQL.QmlUsageTestCase.SimpleQuery

Item {
    id: root
    objectName: "root"
    property bool success: false
    UseSimpleQuery {
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
