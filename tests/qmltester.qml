import QtQuick

Rectangle {
    color: "red"
    objectName: "rootRect"
    anchors.fill: parent
    Loader {
        objectName: "rootLoader"
        anchors.fill: parent
    }
}
