function logHello(extra_string) {
    iface.logMessage("Hello from JS!")
    return extra_string
}

function getLayer(name) {
    return qgisProject.mapLayersByName(name)[0]
}
