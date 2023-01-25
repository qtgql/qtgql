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
        model: EntryPoint.rootQuery.apples
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
            property var apple: model.object
            width: ListView.view.width
            height: 100 + wormsList.implicitHeight
            hoverEnabled: true
            Label {
                id: header
                text: appleDelegate.apple.owner + "'s apple:"
                font.bold: true
            }
            TLabel {
                id: appleIcon
                text: EntryPoint.icons.apple
                color: appleDelegate.apple.color
                font.pointSize: appleDelegate.apple.size
                anchors {
                    right: parent.right
                    top: parent.top
                }
            }
            Button {
                text: "click to remove"
                onClicked: EntryPoint.rootQuery.apples.pop(model.index)
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
                model: appleDelegate.apple.worms
                spacing: 10
                delegate: ItemDelegate {
                    id: wormDelegate
                    width: parent.width
                    required property var model
                    property var worm: model.object
                    Column {
                        Label {
                            text: "family: " + wormDelegate.worm.family
                        }
                        Label {
                            text: "name: " + wormDelegate.worm.name
                        }
                        Label {
                            text: "size: " + wormDelegate.worm.size
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
