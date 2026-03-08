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
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, cast

from PyQt6.QtCore import QObject, QPointF, Qt, QtMsgType, QUrl
from PyQt6.QtQml import QQmlComponent
from PyQt6.QtQuick import QQuickItem

if TYPE_CHECKING:
    from PyQt6.QtQml import QQmlApplicationEngine
    from pytestqt.logging import _QtMessageCapture
    from pytestqt.qtbot import QtBot

    from pytest_qfield.stub_interface.qfield_stubs import QFieldAppInterfaceStub


QML_JS_QOBJECT_TEMPLATE = """
import QtQml
import "{js_file_name}" as Logic

QtObject {{
    function call({params}) {{
        return Logic.{function_name}({params})
    }}
}}

"""


class JsQObject(Protocol):
    """
    Protocol for JavaScript QObject with a call method.
    """

    @staticmethod
    def call(*args: Any) -> Any:  # noqa: ANN401
        """
        Function to call the JavaScript function with the given parameters.
        :param args: Parameters to call the function with.
        :return: A possible return value from the function
        """
        ...


class QFieldBot:
    """
    Helper class for testing QField QML files.
    """

    def __init__(
        self,
        qfield_iface: "QFieldAppInterfaceStub",
        qml_engine: "QQmlApplicationEngine",
        qtbot: "QtBot",
        qtlog: "_QtMessageCapture",
        tmp_path: "Path",
    ) -> None:
        self.iface = qfield_iface
        self._qml_engine = qml_engine
        self.qtbot = qtbot
        self.qtlog = qtlog
        self._tmp_path = tmp_path
        self._plugin_loaded = False

    def show_window(self) -> None:
        """
        Show the QField application window.
        """
        self.iface.show()

    def load_plugin(
        self, qfield_plugin_qml_file: Path, raise_if_warnings: bool = True
    ) -> None:
        """
        Load a QField plugin QML file into the QML engine and wait for it to be loaded.

        :param qfield_plugin_qml_file: Path to the QML file to load.
        :param raise_if_warnings: Whether to raise an exception
                if any warnings or errors are logged during loading.
        """

        self.iface.set_qml_root(
            self.load_qml(qfield_plugin_qml_file, raise_if_warnings)
        )
        self._plugin_loaded = True

    def load_js_function(
        self,
        js_file: Path,
        name: str,
        params: list[str],
        extra_files: list[Path] | None = None,
    ) -> JsQObject:
        """
        Load js function from file as a QObject with function "call".
        Call object.call to execute the function.

        :param js_file: Path to the JavaScript file to load.
        :param name: Name of the function to load.
        :param params: List of parameter names for the function.
        :param extra_files: List of extra files to load.
        :return: JsQObject with the loaded function
        """

        for file in [js_file, *(extra_files if extra_files else [])]:
            shutil.copy(file, self._tmp_path / file.name)
        qml_code = QML_JS_QOBJECT_TEMPLATE.format(
            js_file_name=js_file.name, function_name=name, params=", ".join(params)
        )
        main_qml = self._tmp_path / "main.qml"
        main_qml.touch()
        main_qml.write_text(qml_code)

        component = QQmlComponent(self._qml_engine)
        component.loadUrl(QUrl.fromLocalFile(str(main_qml)))
        js_object = component.create()
        if js_object is None:
            raise ValueError(
                "Could not create QObject with js function: ",
                [error.toString() for error in component.errors()],
            )
        return cast("JsQObject", js_object)

    def get_item(self, object_name: str) -> "QQuickItem":
        self._ensure_plugin_loaded()
        child = self._get_plugin_root_object().findChild(QQuickItem, object_name)
        if not child:
            raise RuntimeError(f"QML object {object_name} not found!")
        return child

    def click_item(
        self,
        item: "QQuickItem",
        mouse_button: Qt.MouseButton = Qt.MouseButton.LeftButton,
    ) -> None:
        center = QPointF(item.width(), item.height()) / 2
        self.qtbot.mouseClick(
            item.window(), mouse_button, pos=item.mapToScene(center).toPoint()
        )

    def load_qml(self, qml_file: Path, raise_if_warnings: bool = True) -> QObject:
        """
        Load a QML file into the QML engine and wait for it to be loaded.

        :param qml_file: Path to the QML file to load.
        :param raise_if_warnings: Whether to raise an exception
                if any warnings or errors are logged during loading.
        """
        initial_log_count = len(self.qtlog.records)
        initial_root_count = len(self._qml_engine.rootObjects())

        if not qml_file.exists():
            raise FileNotFoundError(f"QML file {qml_file} does not exist!")
        with self.qtbot.waitSignal(self._qml_engine.objectCreated):
            self._qml_engine.load(str(qml_file))

        new_logs = [
            (m.type, m.message.strip())
            for m in self.qtlog.records[initial_log_count:]
            if m.type
            in (QtMsgType.QtWarningMsg, QtMsgType.QtCriticalMsg, QtMsgType.QtFatalMsg)
        ]
        if raise_if_warnings and new_logs:
            raise ValueError(f"QML file {qml_file} failed to load:\n{new_logs}")

        if not len(self._qml_engine.rootObjects()) > initial_root_count:
            raise ValueError(f"QML file {qml_file} did not load successfully!")

        return self._qml_engine.rootObjects()[-1]

    def _ensure_plugin_loaded(self) -> None:
        if not self._plugin_loaded:
            raise ValueError("Plugin not loaded yet!")

    def _get_plugin_root_object(self) -> "QObject":
        if not len(self._qml_engine.rootObjects()) > 1:
            raise ValueError("Plugin not loaded yet!")
        # First object is mainWindow
        return self._qml_engine.rootObjects()[1]
