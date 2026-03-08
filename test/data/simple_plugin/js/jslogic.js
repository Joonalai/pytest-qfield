// The imports have to use this .import syntax:
// https://doc.qt.io/qt-6/qtqml-javascript-imports.html#importing-a-qml-module-from-a-javascript-resource

.import "another_file.js" as Another;

function logHello(extra_string) {
    iface.logMessage("Hello from JS!")
    iface.mainWindow().displayToast("Toast!")
    Another.log("Log with another file");
    return extra_string
}

function getLayer(name) {
    return qgisProject.mapLayersByName(name)[0]
}
