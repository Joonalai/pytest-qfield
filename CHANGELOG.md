# CHANGELOG


## v0.6.1 (2026-05-26)

### Bug Fixes

- Pin C++ ownership and retain Python refs for stubs returned to QML
  ([`92d645b`](https://github.com/Joonalai/pytest-qfield/commit/92d645baa25a9b3d59d65e0402ac0886c2d0feb2))


## v0.6.0 (2026-05-22)

### Bug Fixes

- Pin C++ ownership in register_named_item so QML lookups don't reassign
  ([`963c8af`](https://github.com/Joonalai/pytest-qfield/commit/963c8afee97975b0e3299c3907f7444efeec3cd9))

### Features

- Add click_map_at and long_press_map_at QFieldBot helpers
  ([`8bab5bc`](https://github.com/Joonalai/pytest-qfield/commit/8bab5bc8a96a41355ea638a66af04b053b35239e))

- Add featureForm named-item stub
  ([`b55b90e`](https://github.com/Joonalai/pytest-qfield/commit/b55b90e96379936a4ac62ef0057295780abf8a7a))


## v0.5.0 (2026-05-22)

### Features

- Add findItemByObjectName with auto-registered Positioning and GeometryHighlighter stubs
  ([`11e33fe`](https://github.com/Joonalai/pytest-qfield/commit/11e33fef3da0442adb3a28af543177ff7fc5e05d))

- Add QFieldMapCanvasStub with clicked signals and QGIS-backed screenToCoordinate
  ([`1e3ddd1`](https://github.com/Joonalai/pytest-qfield/commit/1e3ddd12f590523f5792cf38af1828d19c794087))


## v0.4.0 (2026-04-06)

### Features

- Add stub for QFieldThemeStub enabling newer QField versions
  ([`81b6973`](https://github.com/Joonalai/pytest-qfield/commit/81b69738adb4d8afb9a8b1fa7f572cb1016dec64))


## v0.3.0 (2026-03-27)

### Bug Fixes

- Fix feature iterator logic
  ([`7864486`](https://github.com/Joonalai/pytest-qfield/commit/7864486efea10ab49ec9611624ab75b910d1162d))

### Features

- Add stub for QgsVectorLayer.getFeature
  ([`0a6d0d2`](https://github.com/Joonalai/pytest-qfield/commit/0a6d0d2f696c8f48445ba61e9f958356eaedf8a9))


## v0.2.4 (2026-03-27)

### Bug Fixes

- Use session fixture to register qml types to avoid Qt limit of 60 registered types
  ([`da17f22`](https://github.com/Joonalai/pytest-qfield/commit/da17f226e4e2c1318bf4be39bd6d3db48decaa31))


## v0.2.3 (2026-03-27)

### Bug Fixes

- Pass correct default value to QgsVectorLayerUtils.createFeature
  ([`d8a4568`](https://github.com/Joonalai/pytest-qfield/commit/d8a456807ba336c301fb62bd6cc22914a549d188))


## v0.2.2 (2026-03-26)

### Bug Fixes

- Fix changelog creation
  ([`3015964`](https://github.com/Joonalai/pytest-qfield/commit/30159644bdb5d2bbd28ae735a495cf4f3f838824))


## v0.2.1 (2026-03-26)

### Features

- Add functionality to open a QField project
  ([`3db9d64`](https://github.com/Joonalai/pytest-qfield/commit/3db9d64dd6d92c3b289a029c2858726f4198989f))

- Use alternative way to sync map layers to show web maps as well
  ([`8b96ae6`](https://github.com/Joonalai/pytest-qfield/commit/8b96ae643c051f1c4a1b1ea65e73294d853dc5d5))


## v0.1.0 (2026-03-24)

- Initial Release
