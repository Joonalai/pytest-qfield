# CHANGELOG


## v0.9.0 (2026-06-12)

### Features

- Add readProject*Entry slots to AppInterface stub
  ([`6f92e7d`](https://github.com/Joonalai/pytest-qfield/commit/6f92e7d26c02a4db350c92226f66f0a97dcd7769))


## v0.8.0 (2026-06-05)

### Features

- Honor open edit session in LayerUtils.deleteFeature stub
  ([`7693025`](https://github.com/Joonalai/pytest-qfield/commit/7693025f2b0f922ed438436624d762f43eb3d5f1))


## v0.7.0 (2026-06-05)

### Features

- Add feature-form lifecycle stubs and QFieldBot helpers
  ([`ae2bbea`](https://github.com/Joonalai/pytest-qfield/commit/ae2bbeab8fc5fb4510ca576ef166cc4ce1f38e05))

- Add LayerUtils.deleteFeature stub slot
  ([`b951706`](https://github.com/Joonalai/pytest-qfield/commit/b951706a6ac484d50aa891a95e6b960c32945280))

- Add settings and focused-occurrence stub surface
  ([`b2c89b2`](https://github.com/Joonalai/pytest-qfield/commit/b2c89b2c83639d57de67fc6d9d1f8854b8d0d7a1))

- Forward edit signals on QgsVectorLayerStub
  ([`a57a28c`](https://github.com/Joonalai/pytest-qfield/commit/a57a28c263cb9ef5aea7c55b0596372cf1f327c4))


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
