import QtQuick
import QtQuick.Controls.Material

Window {
    id: root
    width: 500
    height: 400
    visible: true
    Material.theme: Material.Dark
    Material.accent: Material.Cyan

    Pane {
        anchors.fill: parent
        Loader {
            objectName: "contentloader"
            source: ""
        }
    }
}
