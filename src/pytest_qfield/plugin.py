# Copyright (C) 2026 pytest-qfield Contributors.
#
#
# This file is part of pytest-qfield.
#
# pytest-qfield is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# pytest-qfield is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pytest-qfield.  If not, see <https://www.gnu.org/licenses/>.
import os
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from PyQt6.QtCore import QObject, Qt, QUrl
from PyQt6.QtQml import (
    QQmlApplicationEngine,
    qmlRegisterType,
)
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget
from qgis._core import QgsProject

from pytest_qfield.qfieldbot import QFieldBot
from pytest_qfield.stub_interface.qfield_stubs import (
    QFieldAppInterfaceStub,
    QFieldFeatureUtilsStub,
    QFieldGeometryUtilsStub,
    QFieldLayerUtilsStub,
    QFieldPlatformUtilitiesStub,
    QFieldStringUtilsStub,
)
from pytest_qfield.stub_interface.qgis_stubs import QgsProjectStub, QSettingsStub

if TYPE_CHECKING:
    from _pytest.config import Parser
    from _pytest.fixtures import SubRequest
    from PyQt6.QtWidgets import QApplication
    from pytestqt.logging import _QtMessageCapture
    from pytestqt.qtbot import QtBot
    from qgis.gui import QgisInterface, QgsMapCanvas

_QFIELD_IMPORTS_DIR_ENV = "QFIELD_IMPORTS_DIR"
_QFIELD_IMPORT_DIR_KEY = "qfield_imports_dir"


@pytest.fixture(scope="session")
def qapp_args() -> list[str]:
    return ["QField test"]


@pytest.fixture
def qfield_new_project(qgis_new_project: "QgsProject") -> None:  # noqa: ARG001
    """Initialize new QField project"""
    return


@pytest.fixture
def qfield_bot(  # noqa: PLR0913
    qgis_app: "QApplication",
    qgis_parent: QWidget,
    qgis_canvas: "QgsMapCanvas",
    qfield_iface: QFieldAppInterfaceStub,
    qfield_platform_utilities_stub: QFieldPlatformUtilitiesStub,
    qgs_project_stub: QgsProjectStub,
    qfield_string_utils_stub: QFieldStringUtilsStub,
    qfield_layer_utils_stub: QFieldLayerUtilsStub,
    qfield_feature_utils_stub: QFieldFeatureUtilsStub,
    qfield_geometry_utils_stub: QFieldGeometryUtilsStub,
    register_qfield_resources: None,  # noqa: ARG001
    register_qfield_types: Callable,
    register_qgis_types: Callable,
    main_window_qml_path: Path,
    qtbot: "QtBot",
    qtlog: "_QtMessageCapture",
    request: "SubRequest",
    qfield_qml_extra_context_properties: dict[str, object],
    tmp_path: "Path",
) -> Iterator["QFieldBot"]:
    """Fixture used to create a QFieldBot instance for use during testing."""
    qfield_import_path = _get_qfied_import_path(request)

    engine = QQmlApplicationEngine()

    # Load QField imports
    engine.addImportPath(str(qfield_import_path))

    # Inject QField interface stubs
    qfield_iface.setParent(engine)
    qfield_platform_utilities_stub.setParent(engine)

    system_font_point_size = qgis_app.font().pointSizeF() + 2.0

    # Inject context properties
    context_properties = {
        "iface": qfield_iface,
        "platformUtilities": qfield_platform_utilities_stub,
        "qgisProject": qgs_project_stub,
        "systemFontPointSize": system_font_point_size,
        "settings": QSettingsStub(),
        "StringUtils": qfield_string_utils_stub,
        "LayerUtils": qfield_layer_utils_stub,
        "FeatureUtils": qfield_feature_utils_stub,
        "GeometryUtils": qfield_geometry_utils_stub,
        **qfield_qml_extra_context_properties,
    }

    for property_name, property_value in context_properties.items():
        engine.rootContext().setContextProperty(property_name, property_value)

    register_qfield_types()
    register_qgis_types()

    qfield_bot = QFieldBot(
        qml_engine=engine,
        qfield_iface=qfield_iface,
        qtbot=qtbot,
        qtlog=qtlog,
        tmp_path=tmp_path,
    )

    # Load and embed the QML shell in the pytest-qgis main window.
    qml_overlay_widget, qml_main_window = _load_qml_overlay_widget(
        qml_engine=engine,
        main_window_qml_path=main_window_qml_path,
        parent=qgis_parent,
    )

    _embed_qml_window_in_qgis_main_window(
        qgis_parent=qgis_parent,
        qgis_canvas=qgis_canvas,
        qml_overlay_widget=qml_overlay_widget,
    )

    qfield_iface.set_main_window(
        qgis_main_window=qgis_parent,
        qml_main_window=qml_main_window,
    )
    # Yielding to keep stub instances alive
    yield qfield_bot  # noqa: PT022


@pytest.fixture
def main_window_qml_path() -> Path:
    """
    Path to a file with QML Code of the MainWindow

    Feel free to override this fixture to use a custom QML code for the MainWindow.
    """
    main_window_qml_path = Path(__file__).parent / "main_window.qml"
    if not main_window_qml_path.exists():
        raise FileNotFoundError(
            f"QML path for main_window.qml cannot be found in {main_window_qml_path}!"
        )

    return main_window_qml_path


@pytest.fixture
def qfield_iface(qgis_iface: "QgisInterface") -> QFieldAppInterfaceStub:
    """
    Stub implementation for QFieldAppInterface.

    Override this fixture to use an extended version of the class if needed.
    """
    return QFieldAppInterfaceStub(qgis_iface)


@pytest.fixture
def qfield_platform_utilities_stub() -> QFieldPlatformUtilitiesStub:
    """
    Stub implementation for QFieldPlatformUtilities.

    Override this fixture to use an extended version of the class if needed.
    """
    return QFieldPlatformUtilitiesStub()


@pytest.fixture
def qgs_project_stub() -> QgsProjectStub:
    """
    Stub implementation for QgsProject (qgisProject in QML).

    Override this fixture to use an extended version of the class if needed.
    """
    return QgsProjectStub(QgsProject.instance())


@pytest.fixture
def qfield_string_utils_stub() -> QFieldStringUtilsStub:
    """
    Stub implementation for StringUtils.

    Override this fixture to use an extended version of the class if needed.
    """
    return QFieldStringUtilsStub()


@pytest.fixture(autouse=True)
def qfield_layer_utils_stub() -> Iterator[QFieldLayerUtilsStub]:
    """
    Stub implementation for LayerUtils.

    Override this fixture to use an extended version of the class if needed.
    """
    layer_utils_stub = QFieldLayerUtilsStub()
    yield layer_utils_stub
    iterators = layer_utils_stub.get_iterators()
    try:
        for iterator in iterators:
            if not iterator.closed:
                raise AssertionError("Iterator was not closed")
    finally:
        layer_utils_stub.clear_iterators()


@pytest.fixture
def qfield_feature_utils_stub() -> QFieldFeatureUtilsStub:
    """
    Stub implementation for FeatureUtils.

    Override this fixture to use an extended version of the class if needed.
    """
    return QFieldFeatureUtilsStub()


@pytest.fixture
def qfield_geometry_utils_stub() -> QFieldGeometryUtilsStub:
    """
    Stub implementation for GeometryUtils.

    Override this fixture to use an extended version of the class if needed.
    """
    return QFieldGeometryUtilsStub()


@pytest.fixture
def qfield_qml_extra_context_properties() -> dict[str, object]:
    """
    Override this fixture to provide extra context properties for QField QML files.
    """
    return {}


@pytest.fixture
def register_qfield_resources() -> None:
    """
    Registers compiled resources.
    Override this fixture to provide your own compiled resources.
    """
    # Register /gml
    import pytest_qfield.qfield_resources  # noqa: F401, PLC0415


@pytest.fixture
def register_qfield_types() -> Callable:
    """
    Registers qfield types used in QField plugin.
    Override this fixture to provide more types needed.

    Check this file for a complete list
    (lines that register something to "org.qfield")
    https://github.com/opengisch/QField/blob/master/src/core/qgismobileapp.cpp
    """

    def register_qfield_types() -> None:
        # Something provided here just to get rid of warnings
        qmlRegisterType(QgsProjectStub, "org.qfield", 1, 0, "Foo")
        # qmlRegisterUncreatableType
        # qmlRegisterSingletonType

    return register_qfield_types


@pytest.fixture
def register_qgis_types() -> Callable:
    """
    Registers qgus types used in QField plugin.
    Override this fixture to provide more types needed.

    Check this file for a complete list
    (lines that register something to "org.qgis")
    https://github.com/opengisch/QField/blob/master/src/core/qgismobileapp.cpp
    """

    def register_qgis_types() -> None:
        # Something provided here just to get rid of warnings
        qmlRegisterType(QgsProjectStub, "org.qgis", 1, 0, "Foo")
        # qmlRegisterUncreatableType
        # qmlRegisterSingletonType

    return register_qgis_types


def pytest_addoption(parser: "Parser") -> None:
    parser.addini(
        _QFIELD_IMPORT_DIR_KEY,
        "Absolute path to a directory containing QField imports. "
        "Usually src/qml/imports in QField source code.",
        default=os.getenv(_QFIELD_IMPORTS_DIR_ENV),
    )


def _get_qfied_import_path(request: "SubRequest") -> Path:
    qfield_import_path_config = request.config.getini(
        _QFIELD_IMPORT_DIR_KEY
    ) or os.getenv(_QFIELD_IMPORTS_DIR_ENV)
    if not qfield_import_path_config:
        raise ValueError(
            f"No {_QFIELD_IMPORT_DIR_KEY} ini value "
            f"or {_QFIELD_IMPORTS_DIR_ENV} environment variable set!"
        )

    qfield_import_path = Path(qfield_import_path_config)
    if not qfield_import_path.exists():
        raise ValueError(f"{qfield_import_path} does not exist!")

    if not (qfield_import_path / "Theme").exists():
        raise ValueError(f"{qfield_import_path / 'Theme'} does not exist!")
    return qfield_import_path


def _embed_qml_window_in_qgis_main_window(
    qgis_parent: QWidget,
    qgis_canvas: "QgsMapCanvas",
    qml_overlay_widget: QQuickWidget,
) -> None:
    # Keep QML as a toolbar strip and show QGIS canvas below it.
    # Overlay transparency is not reliable across all Qt backends.
    central_widget = QWidget(parent=qgis_parent)
    central_layout = QVBoxLayout(central_widget)
    central_layout.setContentsMargins(0, 0, 0, 0)
    central_layout.setSpacing(0)

    qml_overlay_widget.setParent(central_widget)
    qml_overlay_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    qml_overlay_widget.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
    )
    qml_overlay_widget.setFixedHeight(56)
    central_layout.addWidget(qml_overlay_widget, 0)

    qgis_canvas.setParent(central_widget)
    qgis_canvas.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
    )
    central_layout.addWidget(qgis_canvas, 1)

    qgis_parent.setCentralWidget(central_widget)


def _load_qml_overlay_widget(
    qml_engine: QQmlApplicationEngine,
    main_window_qml_path: Path,
    parent: QWidget,
) -> tuple[QQuickWidget, QObject]:
    qml_overlay_widget = QQuickWidget(qml_engine, parent)
    surface_format = qml_overlay_widget.format()
    surface_format.setAlphaBufferSize(8)
    qml_overlay_widget.setFormat(surface_format)
    qml_overlay_widget.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
    qml_overlay_widget.setAutoFillBackground(False)
    qml_overlay_widget.setClearColor(Qt.GlobalColor.transparent)
    qml_overlay_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
    qml_overlay_widget.setStyleSheet("background: transparent;")
    qml_overlay_widget.setSource(QUrl.fromLocalFile(str(main_window_qml_path)))

    if qml_overlay_widget.status() == QQuickWidget.Status.Error:
        errors = [error.toString() for error in qml_overlay_widget.errors()]
        raise ValueError(f"QML file {main_window_qml_path} failed to load: {errors}")

    root_object = qml_overlay_widget.rootObject()
    if root_object is None:
        raise ValueError(f"QML file {main_window_qml_path} did not load successfully!")
    return qml_overlay_widget, root_object
