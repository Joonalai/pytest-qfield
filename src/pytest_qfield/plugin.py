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
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from PyQt6.QtQml import QQmlApplicationEngine

from pytest_qfield.qfieldbot import QFieldBot
from pytest_qfield.stub_interface import (
    QFieldAppInterfaceStub,
    QFieldPlatformUtilitiesStub,
    QgsProjectStub,
    QSettingsStub,
)

if TYPE_CHECKING:
    from _pytest.config import Parser
    from _pytest.fixtures import SubRequest
    from PyQt6.QtWidgets import QApplication
    from pytestqt.logging import _QtMessageCapture
    from pytestqt.qtbot import QtBot

_QFIELD_IMPORTS_DIR_ENV = "QFIELD_IMPORTS_DIR"
_QFIELD_IMPORT_DIR_KEY = "qfield_imports_dir"


@pytest.fixture(scope="session")
def qapp_args() -> list[str]:
    return ["QField test"]


@pytest.fixture
def qfield_bot(  # noqa: PLR0913
    qapp: "QApplication",
    qfield_iface: QFieldAppInterfaceStub,
    qfield_platform_utilities_stub: QFieldPlatformUtilitiesStub,
    qgs_project_stub: QgsProjectStub,
    main_window_qml_path: Path,
    qtbot: "QtBot",
    qtlog: "_QtMessageCapture",
    request: "SubRequest",
    qfield_qml_extra_context_properties: dict[str, object],
    tmp_path: "Path",
) -> "QFieldBot":
    """Fixture used to create a QFieldBot instance for using during testing."""
    qfield_import_path = _get_qfied_import_path(request)

    engine = QQmlApplicationEngine()

    # Load QField imports
    engine.addImportPath(str(qfield_import_path))

    # Inject QField interface stubs
    qfield_iface.setParent(engine)
    qfield_platform_utilities_stub.setParent(engine)

    system_font_point_size = qapp.font().pointSizeF() + 2.0

    # Inject context properties
    context_properties = {
        "iface": qfield_iface,
        "platformUtilities": qfield_platform_utilities_stub,
        "qgisProject": qgs_project_stub,
        "systemFontPointSize": system_font_point_size,
        "settings": QSettingsStub(),
        **qfield_qml_extra_context_properties,
    }

    for property_name, property_value in context_properties.items():
        engine.rootContext().setContextProperty(property_name, property_value)

    qfield_bot = QFieldBot(
        qml_engine=engine,
        qfield_iface=qfield_iface,
        qtbot=qtbot,
        qtlog=qtlog,
        tmp_path=tmp_path,
    )

    # Load the main window
    qfield_iface.set_main_window(qfield_bot.load_qml(main_window_qml_path))

    return qfield_bot


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
def qfield_iface() -> QFieldAppInterfaceStub:
    """
    Stub implementation for QFieldAppInterface.

    Override this fixture to use an extended version of the class if needed.
    """
    return QFieldAppInterfaceStub()


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
    return QgsProjectStub()


@pytest.fixture
def qfield_qml_extra_context_properties() -> dict[str, object]:
    """
    Override this fixture to provide extra context properties for QField QML files.
    """
    return {}


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
