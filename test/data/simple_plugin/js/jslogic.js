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
    const layer = qgisProject.mapLayersByName(name)[0];
    if (layer && layer.isValid) {
        iface.logMessage(`Layer ${layer.name} is valid!`);
    }
    return layer
}

function sum(x, y) {
    iface.logMessage(`Summing ${x} and ${y}`)
    return x + y
}
