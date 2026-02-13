import QtQuick
import Theme

Item {
    property var mainWindow: iface.mainWindow()

    Component.onCompleted: {
        iface.addItemToPluginsToolbar(pluginButton);
    }

    QfToolButton {
        id: pluginButton
        objectName: "pluginButton"

        bgcolor: Theme.darkGray
        iconSource: "icon.svg"
        iconColor: Theme.mainColor
        round: true
        onClicked: {
            iface.logMessage("Plugin button clicked!");
        }
    }

}
