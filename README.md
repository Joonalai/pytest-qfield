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
| `qfield_string_utils_stub` | `StringUtils` | String utility functions. |
| `qfield_layer_utils_stub` | `LayerUtils` | Layer utility functions. |
| `qfield_feature_utils_stub` | `FeatureUtils` | Feature utility functions. |
| `qfield_geometry_utils_stub` | `GeometryUtils` | Geometry utility functions. |
| `qfield_qml_extra_context_properties` | (various) | Dictionary of extra context properties to inject. |

#### How to Override

To override a stub or another fixture, define it in your project's `conftest.py`:

```python
# conftest.py
import pytest
from pytest_qfield.stub_interface.qfield_stubs import QFieldAppInterfaceStub

class CustomIface(QFieldAppInterfaceStub):
    def some_custom_method(self):
        return "custom value"

@pytest.fixture
def qfield_iface(qgis_iface):
    return CustomIface(qgis_iface)
```

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
- `show_window()`: Shows the QField main window.
- `get_item(object_name)`: Finds a QML item by its `objectName`.
- `click_item(item)`: Simulates a mouse click on a QML item.
- `load_js_function(js_file, function_name, params)`: Loads a JavaScript function from a file for direct testing.

## Examples

- Basic plugin loading/clicking tests: [`test/test_plugin.py`](test/test_plugin.py)
- Javascript function tests: [`test_javascript_functions.py`](test/test_javascript_functions.py)
- Stub interface integration: [`test/test_stub_interface.py`](test/test_stub_interface.py)
- Visual/manual checks: [`test/visual/test_plugin_visually.py`](test/visual/test_plugin_visually.py)

## Installation

Install with `pip` or `uv`:

```bash
pip install pytest-qfield
# uv add --dev pytest-qfield
```

### Configure QField imports path

The plugin needs access to QField source code for its QML imports (typically `QField/src/qml/imports`).

First clone [QField](https://github.com/opengisch/QField) source code somewhere and checkout the `v4.0.6` tag and then
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

- Clone [QField](https://github.com/opengisch/QField) source code somewhere and checkout the `v4.0.6` tag
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

## Contributing

Contributions are very welcome.

## Inspirations

- [pytest-qgis](https://github.com/osgeosuomi/pytest-qgis)
- [pytest-qt](https://github.com/pytest-dev/pytest-qt)
- [This Stackoverflow answer](https://stackoverflow.com/a/71832084)

## License

Distributed under the terms of the `GNU GPL v2.0` license, "pytest-qfield" is free and open source software.
