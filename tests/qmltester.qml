import QtQuick
import QtQuick.Controls.Material

Window {
    id: root
    width: 500
    height: 400
    visible: true
    Material.theme: Material.Dark
    Material.accent: Material.Cyan
    objectName: "rootWindow"
    Pane {
        objectName: "MainPane"
        anchors.fill: parent
        Loader {
            objectName: "contentloader"
            anchors.fill: parent
        }
    }
}
