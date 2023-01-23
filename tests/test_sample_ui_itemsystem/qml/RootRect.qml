import QtQuick
import QtQuick.Controls.Material
import com.props 1.0

Pane {
    id: root
    FontLoader {
        id: fonts
        source: "./materialdesignicons-webfont.ttf"
    }

    ListView {
        height: parent.height
        width: 400
        anchors.centerIn: parent
        model: EntryPoint.appleModel
        removeDisplaced: Transition {
            NumberAnimation {
                properties: "x, y"
                duration: 400
            }
        }
        remove: Transition {
            ParallelAnimation {
                NumberAnimation {
                    property: "opacity"
                    to: 0
                    duration: 400
                }
                NumberAnimation {
                    properties: "x, y"
                    to: 100
                    duration: 400
                }
            }
        }
        delegate: ItemDelegate {
            id: appleDelegate
            required property var model
            width: ListView.view.width
            height: 100 + wormsList.implicitHeight
            hoverEnabled: true
            Text {
                text: model.p_class.prop
                color: "red"
                anchors.right: parent.right
            }
            Label {
                id: header
                text: appleDelegate.model.owner + "'s apple:"
                font.bold: true
            }
            TLabel {
                id: appleIcon
                text: EntryPoint.icons.apple
                color: appleDelegate.model.color
                font.pointSize: appleDelegate.model.size
                anchors {
                    right: parent.right
                    top: parent.top
                }
            }
            Button {
                text: "click to remove"
                onClicked: EntryPoint.appleModel.pop(model.index)
                anchors.bottom: parent.bottom
                enabled: parent.hovered
            }
            ListView {
                id: wormsList
                implicitHeight: contentItem.height
                width: parent.width - appleIcon.width - 10
                anchors {
                    top: header.bottom
                }
                header: Label {
                    text: wormsList.count ? 'Worms:' : 'No worms!'
                }
                model: appleDelegate.model.worms
                spacing: 10
                delegate: ItemDelegate {
                    id: wormDelegate
                    width: parent.width
                    required property var model
                    Column {
                        Label {
                            text: "family: " + wormDelegate.model.family
                        }
                        Label {
                            text: "name: " + wormDelegate.model.name
                        }
                        Label {
                            text: "size: " + wormDelegate.model.size
                        }
                    }
                    TLabel {
                        text: EntryPoint.icons.ladybug
                        color: "pink"
                        anchors.right: parent.right
                    }
                }
            }
        }
    }
}
