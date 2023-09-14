import QtQuick
// import GraphQL.QmlUsage.SimpleQuery
//
// Item {
//     id: root
//     objectName: "root"
//     property bool success: false
//     UseSimpleQuery {
//         id: main_query
//         onCompletedChanged: root.success = true
//     }
//     Component.onCompleted: {
//         main_query.fetch();
//     }
//     Text {
//         text: `completed ${main_query.completed}`
//     }
// }
Rectangle{
    width: 200;
    height: 299;
    color: "blue";
}
