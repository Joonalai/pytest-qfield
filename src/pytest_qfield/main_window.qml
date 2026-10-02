import QtQuick
import Theme

Item {
    id: root

    property var toastMessages: []
    property string currentToastMessage: ""
    property int nextToastIndex: 0
    // QField overlays parent to mainWindow.contentItem, which covers the map.
    property alias contentItem: contentArea

    function displayToast(message) {
        toastMessages.push(message);

        if (!toastTimer.running && !toastContainer.visible) {
            showNextToast();
        }
    }

    function showNextToast() {
        if (nextToastIndex >= toastMessages.length) {
            currentToastMessage = "";
            toastContainer.visible = false;
            return;
        }

        currentToastMessage = toastMessages[nextToastIndex];
        nextToastIndex += 1;
        toastContainer.visible = true;
        toastTimer.restart();
    }

    objectName: "mainWindow"
    width: 640
    height: 480

    Item {
        id: host

        objectName: "host"
        anchors.fill: parent
    }

    Rectangle {
        id: toolbar

        objectName: "pluginsToolbar"
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 50
        color: "#333333"

        Row {
            id: toolbarRow

            objectName: "pluginsToolbarRow"
            anchors.fill: parent
            anchors.margins: 6
            spacing: 6
        }

    }

    Item {
        id: contentArea

        objectName: "contentItem"
        anchors.fill: parent
    }

    Rectangle {
        id: toastContainer

        visible: false
        z: 1000
        radius: 8
        color: Theme.secondaryTextColor
        border.color: "#66000000"
        border.width: 1

        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 24

        width: Math.min(root.width - 32, toastText.implicitWidth + 32)
        height: toastText.implicitHeight + 20

        Text {
            id: toastText

            anchors.centerIn: parent
            width: parent.width - 24
            text: root.currentToastMessage
            color: "white"
            wrapMode: Text.Wrap
            horizontalAlignment: Text.AlignHCenter
        }
    }

    Timer {
        id: toastTimer

        interval: 2500
        repeat: false
        onTriggered: {
            toastContainer.visible = false;
            root.showNextToast();
        }
    }

}
