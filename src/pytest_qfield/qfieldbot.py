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

from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtCore import QPointF, Qt, QtMsgType
from PyQt6.QtQuick import QQuickItem

if TYPE_CHECKING:
    from PyQt6.QtQml import QQmlApplicationEngine
    from pytestqt.logging import _QtMessageCapture
    from pytestqt.qtbot import QtBot

    from pytest_qfield.stub_interface import QFieldAppInterfaceStub


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
    ) -> None:
        self.iface = qfield_iface
        self._qml_engine = qml_engine
        self.qtbot = qtbot
        self.qtlog = qtlog
        self._plugin_loaded = False

    def load_plugin(
        self, qfield_plugin_qml_file: Path, raise_if_warnings: bool = True
    ) -> None:
        """
        Load a QField plugin QML file into the QML engine and wait for it to be loaded.

        :param qfield_plugin_qml_file: Path to the QML file to load.
        :param raise_if_warnings: Whether to raise an exception
                if any warnings or errors are logged during loading.
        """
        self.load_qml(qfield_plugin_qml_file, raise_if_warnings)
        self.iface.set_qml_root(self._qml_engine.rootObjects()[0])
        self._plugin_loaded = True

    def get_item(self, object_name: str) -> "QQuickItem":
        self._ensure_plugin_loaded()
        child = self._qml_engine.rootObjects()[0].findChild(QQuickItem, object_name)
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

    def load_qml(self, qml_file: Path, raise_if_warnings: bool = True) -> None:
        """
        Load a QML file into the QML engine and wait for it to be loaded.

        :param qml_file: Path to the QML file to load.
        :param raise_if_warnings: Whether to raise an exception
                if any warnings or errors are logged during loading.
        """
        initial_log_count = len(self.qtlog.records)

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

        if not len(self._qml_engine.rootObjects()) > 0:
            raise RuntimeError(f"QML file {qml_file} did not load successfully!")

    def _ensure_plugin_loaded(self) -> None:
        if not self._plugin_loaded:
            raise RuntimeError("Plugin not loaded yet!")
