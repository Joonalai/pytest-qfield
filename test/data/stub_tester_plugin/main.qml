import QtQuick
import Theme
import org.qgis
import org.qfield

import "qrc:/qml" as QFieldItems

Item {
    property var mainWindow: iface.mainWindow()
    property var mapCanvas: iface.mapCanvas()
    property string layerName: "points"
    property var pointLayer: null

    Connections {
        target: mapCanvas
        ignoreUnknownSignals: true
        function onClicked(point, type) {
            const coord = mapCanvas.mapSettings.screenToCoordinate(point);
            iface.logMessage(`clicked x: ${coord.x}`);
            iface.logMessage(`clicked y: ${coord.y}`);
            iface.logMessage(`clicked type: ${type}`);
        }
        function onConfirmedClicked(point, type) {
            const coord = mapCanvas.mapSettings.screenToCoordinate(point);
            iface.logMessage(`confirmed x: ${coord.x}`);
            iface.logMessage(`confirmed y: ${coord.y}`);
        }
    }

    Component.onCompleted: {
        iface.addItemToPluginsToolbar(button1);
        iface.addItemToPluginsToolbar(button2);
        iface.addItemToPluginsToolbar(button3);
        iface.addItemToPluginsToolbar(button4);
        iface.addItemToPluginsToolbar(button5);
        iface.addItemToPluginsToolbar(button6);

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

    QfToolButton {
        id: button3
        objectName: "test_position_source"

        bgcolor: Theme.darkGray
        iconSource: "icon.svg"
        iconColor: Theme.mainColor
        round: true
        onClicked: {
            const positionSource = iface.findItemByObjectName("positionSource");
            if (!positionSource) {
                iface.logMessage("positionSource not found");
                return;
            }
            iface.logMessage(`positionSource active: ${positionSource.active}`);
            const pos = positionSource.projectedPosition;
            iface.logMessage(`positionSource x: ${pos.x}`);
            iface.logMessage(`positionSource y: ${pos.y}`);
        }
    }

    QfToolButton {
        id: button4
        objectName: "test_geometry_highlighter"

        bgcolor: Theme.darkGray
        iconSource: "icon.svg"
        iconColor: Theme.mainColor
        round: true
        onClicked: {
            const highlighter = iface.findItemByObjectName("geometryHighlighter");
            if (!highlighter) {
                iface.logMessage("geometryHighlighter not found");
                return;
            }
            highlighter.geometryWrapper.qgsGeometry = GeometryUtils.createGeometryFromWkt("POINT(1 2)");
            highlighter.duration = 1500;
            highlighter.visible = true;
            highlighter.update();
            iface.logMessage(`highlighter visible: ${highlighter.visible}`);
            iface.logMessage(`highlighter duration: ${highlighter.duration}`);
            iface.logMessage(`highlighter geometry: ${highlighter.geometryWrapper.qgsGeometry.asWkt(0)}`);
            highlighter.geometryWrapper.clear();
            iface.logMessage(`highlighter geometry after clear: ${highlighter.geometryWrapper.qgsGeometry}`);
        }
    }

    QfToolButton {
        id: button6
        objectName: "test_project_entries"

        bgcolor: Theme.darkGray
        iconSource: "icon.svg"
        iconColor: Theme.mainColor
        round: true
        onClicked: {
            iface.logMessage(`entry: ${iface.readProjectEntry("test", "stringKey", "fallback")}`);
            iface.logMessage(`num: ${iface.readProjectNumEntry("test", "numKey", -1)}`);
            iface.logMessage(`double: ${iface.readProjectDoubleEntry("test", "doubleKey", -1.5)}`);
            iface.logMessage(`bool: ${iface.readProjectBoolEntry("test", "boolKey", false)}`);
            iface.logMessage(`missing entry: ${iface.readProjectEntry("test", "missingKey", "fallback")}`);
            iface.logMessage(`missing num: ${iface.readProjectNumEntry("test", "missingKey", -1)}`);
            iface.logMessage(`missing double: ${iface.readProjectDoubleEntry("test", "missingKey", -1.5)}`);
            iface.logMessage(`missing bool: ${iface.readProjectBoolEntry("test", "missingKey", true)}`);
        }
    }

    QfToolButton {
        id: button5
        objectName: "test_unknown_named_item"

        bgcolor: Theme.darkGray
        iconSource: "icon.svg"
        iconColor: Theme.mainColor
        round: true
        onClicked: {
            const unknown = iface.findItemByObjectName("doesNotExist");
            iface.logMessage(`unknown is null: ${unknown === null}`);
        }
    }

}
