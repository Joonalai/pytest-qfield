# pytest-qfield

A [pytest](https://docs.pytest.org) plugin for testing [QField](https://github.com/opengisch/QField) QML plugins. This
plugin uses [`pytest-qgis`](https://github.com/osgeosuomi/pytest-qgis) and QGIS behind the hood since QField does not
have a python api.

## Features

### Fixtures

The following fixtures are provided by `pytest-qfield`:

- `qfield_bot`: A `QFieldBot` instance to interact with the QField QML environment.
- `qfield_iface`: A stub implementation of the QField application interface (`iface` in QML).
- `qfield_new_project`: Initializes a new QField project.
- `main_window_qml_path`: Path to the QML file used for the QField main window. Can be overridden to use a custom QML main window.

### Stubs and Overriding Fixtures

`pytest-qfield` provides several stub fixtures that are automatically injected into the QML engine's context. You can override these fixtures in your `conftest.py` to provide custom behavior or extended versions of the stub classes.

#### Available Stubs

The following stub fixtures correspond to objects available in the QField QML context:

| Fixture Name | QML Context Property | Description |
| --- | --- | --- |
| `qfield_iface` | `iface` | QField application interface. |
| `qgs_project_stub` | `qgisProject` | QgsProject instance. |
| `qfield_platform_utilities_stub` | `platformUtilities` | Platform-specific utilities. |
| `qfield_theme_stub` | `Theme` | Theme colors, fonts, and layout constants. Required for QField versions >v4.0.6 where Theme is a C++ singleton. |
| `qfield_string_utils_stub` | `StringUtils` | String utility functions. |
| `qfield_layer_utils_stub` | `LayerUtils` | Layer utility functions. |
| `qfield_feature_utils_stub` | `FeatureUtils` | Feature utility functions. |
| `qfield_geometry_utils_stub` | `GeometryUtils` | Geometry utility functions. |
| `qfield_qml_extra_context_properties` | (various) | Dictionary of extra context properties to inject. |

#### Named-Item Stubs

Some QField QML code locates objects through `iface.findItemByObjectName("...")` rather than as context properties. `pytest-qfield` auto-registers default stubs on the iface for the following object names:

| Fixture Name | Registered `objectName` | Description |
| --- | --- | --- |
| `qfield_positioning_stub` | `positionSource` | QField `Positioning` item — `active` flag and `projectedPosition` (x, y). |
| `qfield_geometry_highlighter_stub` | `geometryHighlighter` | `GeometryHighlighter` exposing `geometryWrapper`, `duration`, `visible`, and `update()`. |
| `qfield_feature_list_form_stub` | `featureForm` | `FeatureListForm` — drive an existing feature's attribute form via `model.setFeatures(layer, filter)`, `selection.focusedItem`, `state` (`"Hidden"` / `"FeatureList"` / `"FeatureForm"` read-only view / `"FeatureFormEdit"` edit), and `visible` (true whenever a feature is shown). The QML id is `featureListForm` but plugins look it up by `objectName` `"featureForm"`. |
| `qfield_overlay_feature_form_drawer_stub` | `overlayFeatureFormDrawer` | `overlayFeatureFormDrawer` — the drawer that covers the map after digitizing a feature. Exposes `opened`. Distinct from `featureForm`. |

For the form stub, tests typically drive the canonical pattern from QML and assert on the captured calls:

```js
// in your plugin's QML
const form = iface.findItemByObjectName("featureForm");
form.model.setFeatures(layer, "id = '" + uuid + "'");
form.selection.focusedItem = 0;
form.state = "FeatureFormEdit";
```

```python
def test_form_was_opened(qfield_feature_list_form_stub):
    (recorded_layer, recorded_filter), = (
        qfield_feature_list_form_stub.model.set_features_calls
    )
    assert recorded_layer.name == "points"
    assert recorded_filter == "id = 'abc'"
    assert qfield_feature_list_form_stub.state == "FeatureFormEdit"
```

Override the relevant fixture to inject custom values (e.g. a fixed position):

```python
# conftest.py
import pytest
from pytest_qfield.stub_interface.qfield_stubs import QFieldPositioningStub

@pytest.fixture
def qfield_positioning_stub() -> QFieldPositioningStub:
    return QFieldPositioningStub(x=389870.0, y=6678167.0, active=True)
```

See [`test/test_named_item_overrides.py`](test/test_named_item_overrides.py) for a complete working example. To assert behaviour when a named item is *missing*, clear the registration on the iface stub or override the fixture to return a sentinel.

#### Map Canvas Stub

`iface.mapCanvas()` returns a `QFieldMapCanvasStub` exposing the QField `MapCanvas` signals plugins listen to:

| Member | Description |
| --- | --- |
| `clicked(QPointF, int)` signal | Emitted by QField when the user taps the map. |
| `confirmedClicked(QPointF, int)` signal | Emitted on a long-press / confirmed tap. |
| `mapSettings.screenToCoordinate(QPointF) -> QPointF` | Delegates to the wired `QgsMapCanvas.mapSettings().mapToPixel()` for real screen→CRS projection (identity fallback when no canvas is wired). |

The stub is auto-attached to the iface as `qml_map_canvas` and is also exposed via the `qfield_map_canvas_stub` fixture for overrides. By default the fixture wires `pytest-qgis`'s `qgis_canvas` so projection works for real — set an extent and size on `qgis_canvas`, then drive clicks at project-CRS coordinates with `qfield_bot.click_map_at` / `long_press_map_at`:

```python
from qgis.core import QgsPointXY, QgsRectangle

def test_pick_end_point(qfield_bot, qgis_canvas):
    qgis_canvas.show()
    qgis_canvas.resize(200, 200)
    qgis_canvas.setExtent(QgsRectangle(0, 0, 1000, 1000))
    qgis_canvas.refresh()

    qfield_bot.click_map_at(QgsPointXY(500.0, 500.0))
    # ...assert your plugin reacted to the picked CRS coordinate

    # confirmedClicked (QField's long-press) and non-default click types:
    qfield_bot.long_press_map_at(QgsPointXY(500.0, 500.0))
    qfield_bot.click_map_at(QgsPointXY(0.0, 0.0), click_type=1)
```

Both helpers invert the live `mapSettings.mapToPixel()` transform before emitting, so a plugin handler that does `mapSettings.screenToCoordinate(point)` recovers the CRS coordinate you passed in.

If you need to emit a raw screen-space click (or you've opted out of canvas wiring), reach the signal directly:

```python
from PyQt6.QtCore import QPointF

qfield_bot.iface.qml_map_canvas.clicked.emit(QPointF(0.0, 0.0), 0)
```

If you'd rather skip the canvas setup and pass project-CRS coordinates directly, override the fixture to drop canvas wiring:

```python
@pytest.fixture
def qfield_map_canvas_stub() -> QFieldMapCanvasStub:
    return QFieldMapCanvasStub()  # no canvas → identity screenToCoordinate
```

For richer modelling (custom signals, an `extent` property, etc.), subclass `QFieldMapCanvasStub` / `QFieldMapSettingsStub` and return your subclass from the fixture.

#### How to Override

To override a stub, subclass it and redefine the fixture in your `conftest.py` or test module.
For example, to make `StringUtils.createUuid()` return a deterministic value:

```python
# conftest.py
import pytest
from PyQt6.QtCore import pyqtSlot
from pytest_qfield.stub_interface.qfield_stubs import QFieldStringUtilsStub

class DeterministicStringUtils(QFieldStringUtilsStub):
    @pyqtSlot(result=str)
    def createUuid(self) -> str:
        return "{00000000-0000-0000-0000-000000000000}"

@pytest.fixture
def qfield_string_utils_stub() -> QFieldStringUtilsStub:
    return DeterministicStringUtils()
```

Any QML code calling `StringUtils.createUuid()` will now receive the fixed value.
See [`test/test_fixture_override.py`](test/test_fixture_override.py) for a complete working example.

You can also use `qfield_qml_extra_context_properties` to inject additional objects into the QML context:

```python
@pytest.fixture
def qfield_qml_extra_context_properties():
    return {
        "myCustomObject": MyCustomObject()
    }
```

Other overridable fixtures include:

- `main_window_qml_path`: Override to use a different QML file as the main window shell.
- `register_qfield_resources`: Override to register your own compiled Qt resources (`.qrc`).
- `register_qfield_types`: Override to register additional QML types.
- `register_qgis_types`: Override to register additional QGIS-related QML types.

## QFieldBot

The `qfield_bot` fixture provides several methods to help testing:

- `load_plugin(qml_file)`: Loads a QField plugin QML file.
- `open_project(qfield_project_file)`: Opens a QField project file.
- `show_window()`: Shows the QField main window.
- `get_item(object_name)`: Finds a QML item by its `objectName`.
- `click_item(item)`: Simulates a mouse click on a QML item.
- `click_map_at(crs_point, click_type=0)`: Emits `clicked` on the QML map canvas stub for a tap at a project-CRS coordinate (inverts `mapToPixel` so the plugin's `screenToCoordinate` recovers the input).
- `long_press_map_at(crs_point, click_type=0)`: Emits `confirmedClicked` (QField's long-press gesture) at a project-CRS coordinate.
- `open_feature_form(layer, feature_id, mode="view")`: Drives the `featureForm` stub as QField does when a feature is opened — navigates the model to the feature, sets `state` to the read-only `"FeatureForm"` view (`mode="view"`) or `"FeatureFormEdit"` (`mode="edit"`), and makes the form `visible`. Notify signals fire so bound plugin QML reacts.
- `open_overlay_form(layer, feature_id)`: Opens the `overlayFeatureFormDrawer` stub (`opened = True`) for a feature, as QField does after digitizing.
- `close_forms()`: Hides `featureForm` (`visible = False`, `state = "Hidden"`) and closes `overlayFeatureFormDrawer` (`opened = False`).
- `load_js_function(js_file, function_name, params)`: Loads a JavaScript function from a file for direct testing.

## Examples

- Basic plugin loading/clicking tests: [`test/test_plugin.py`](test/test_plugin.py)
- Overriding stub fixtures: [`test/test_fixture_override.py`](test/test_fixture_override.py)
- Overriding auto-registered named-item stubs: [`test/test_named_item_overrides.py`](test/test_named_item_overrides.py)
- Driving the feature-form lifecycle: [`test/test_feature_form_lifecycle.py`](test/test_feature_form_lifecycle.py)
- Javascript function tests: [`test/test_javascript_functions.py`](test/test_javascript_functions.py)
- Stub interface integration: [`test/test_stub_interface.py`](test/test_stub_interface.py)
- Visual/manual checks: [`test/visual/test_plugin_visually.py`](test/visual/test_plugin_visually.py)

## Installation

You must have QGIS >= 4.0 installed to use this plugin.

Install with `pip` or `uv` to a python environment that is aware of system QGIS libraries.
You can create one with [qgis-venv-creator](https://github.com/GispoCoding/qgis-venv-creator).

```bash
pip install pytest-qfield
# uv add --dev pytest-qfield
```

### Configure QField imports path

The plugin needs access to QField source code for its QML imports (typically `QField/src/qml/imports`).

First clone [QField](https://github.com/opengisch/QField) source code somewhere and checkout the target QField tag and then
set it either with an environment variable or a `pytest.ini` value.

```bash
QFIELD_IMPORTS_DIR=/absolute/path/to/QField/src/qml/imports pytest
```

```ini
# pyproject.toml
[tool.pytest.ini_options]
qfield_imports_dir = /absolute/path/to/QField/src/qml/imports
```

## Development environment

This project uses [uv](https://docs.astral.sh/uv/getting-started/installation/)
to manage python packages. Make sure to have it installed first.

- Clone [QField](https://github.com/opengisch/QField) source code somewhere and checkout the tag for requested QField version.
- Copy .env.example to .env and fill the missing values
- Create a venv that is aware of system QGIS libraries: `uv venv --system-site-packages`. Make sure to use same Python
  executable as QGIS.
    - On Windows, maybe use a tool like [qgis-venv-creator](https://github.com/GispoCoding/qgis-venv-creator).

```shell
# Activate the virtual environment
$ source .venv/bin/activate
# Install dependencies
$ uv sync
# Install pre-commit hooks
$ prek install
# Run tests
$ uv run pytest
```

### Updating dependencies

`uv lock --upgrade`

### Release process

Releases are made automatically upon push to main branch using Python Semantic Release.

## Contributing

Contributions are very welcome.

## Inspirations

- [pytest-qgis](https://github.com/osgeosuomi/pytest-qgis)
- [pytest-qt](https://github.com/pytest-dev/pytest-qt)
- [This Stackoverflow answer](https://stackoverflow.com/a/71832084)

## License

Distributed under the terms of the `GNU GPL v2.0` license, "pytest-qfield" is free and open source software.
