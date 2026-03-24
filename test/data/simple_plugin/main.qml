import QtQuick
import Theme
import org.qgis
import org.qfield

import "qrc:/qml" as QFieldItems

Item {
    property var mainWindow: iface.mainWindow()

    Component.onCompleted: {
        iface.addItemToPluginsToolbar(pluginButton);

        function projectLoaded() {
            iface.logMessage("Project load ended");
        }

        iface.loadProjectEnded.connect(projectLoaded);
    }

    QfToolButton {
        id: pluginButton
        objectName: "pluginButton"

        bgcolor: Theme.darkGray
        iconSource: "icon.svg"
        iconColor: Theme.mainColor
        round: true
        onClicked: {
            const value = StringUtils.createUuid();

            iface.logMessage("Plugin button clicked!");
            iface.logMessage("UUID value:", value);
            iface.mainWindow().displayToast("Toast displayed!")
        }
    }

}
