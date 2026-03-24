import QtQuick
import Theme
import org.qgis
import org.qfield

import "qrc:/qml" as QFieldItems

Item {
    property var mainWindow: iface.mainWindow()
    property string layerName: "points"
    property var pointLayer: null

    Component.onCompleted: {
        iface.addItemToPluginsToolbar(button1);
        iface.addItemToPluginsToolbar(button2);

        function setup() {
            pointLayer = qgisProject.mapLayersByName(layerName)[0];
            if (!pointLayer || !pointLayer.isValid) {
                iface.logMessage("Layer not loaded");
                return
            }
            pointLayer.featureAdded.connect((fid) => iface.logMessage(`Feature added: ${fid}`));
            iface.logMessage("Setup complete");
        }


        iface.loadProjectEnded.connect(setup)
    }

    QfToolButton {
        id: button1
        objectName: "test_creating_feature"

        bgcolor: Theme.darkGray
        iconSource: "icon.svg"
        iconColor: Theme.mainColor
        round: true
        onClicked: {
            let success = false;
            const geometry = GeometryUtils.createGeometryFromWkt("POINT(1.5 2.4)");
            iface.logMessage(`Geometry: ${geometry.asWkt(0)}`);

            const feature = FeatureUtils.createFeature(pointLayer, geometry);
            iface.logMessage("Feature created");

            feature.setAttribute("text_field", "new_value")

            success = pointLayer.startEditing()
            iface.logMessage(`Editing started: ${success}`);

            success = LayerUtils.addFeature(pointLayer, feature);
            iface.logMessage(`Feature added: ${success}`);

            success = pointLayer.commitChanges()
            iface.logMessage(`Committed changes: ${success}`);
        }
    }

    QfToolButton {
        id: button2
        objectName: "test_feature_iterator"

        bgcolor: Theme.darkGray
        iconSource: "icon.svg"
        iconColor: Theme.mainColor
        round: true
        onClicked: {
            let success = false;
            const expression = "text_field = 'test'";
            const iterator = LayerUtils.createFeatureIteratorFromExpression(pointLayer, expression);
            try {
                if (iterator.hasNext()) {
                    const feature = iterator.next();
                    iface.logMessage(`Feature found: ${feature.id}`)
                    iface.logMessage(`Geometry: ${feature.geometry.asWkt(0)}`)
                }
            } finally {
                iterator.close();
            }



        }
    }

}
