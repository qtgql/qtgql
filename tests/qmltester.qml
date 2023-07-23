import QtQuick
import QtQuick.Controls.Material

Rectangle {
    color: "grey"
    objectName: "MainPane"
    anchors.fill: parent
    Loader {
        objectName: "contentloader"
        anchors.fill: parent
    }
}
