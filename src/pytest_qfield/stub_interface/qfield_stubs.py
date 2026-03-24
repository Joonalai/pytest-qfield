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
import uuid
from typing import TYPE_CHECKING

from PyQt6.QtCore import QObject, QSizeF, pyqtSignal, pyqtSlot
from PyQt6.QtQuick import QQuickItem

if TYPE_CHECKING:
    from qgis.gui import QgisInterface


class QFieldAppInterfaceStub(QObject):
    """
    Stub implementation of AppInterface.

    https://api.qfield.org/QField/classAppInterface/
    """

    loadProjectEnded = pyqtSignal()  # noqa: N815

    def __init__(self, qgis_iface: "QgisInterface") -> None:
        super().__init__(parent=None)
        self.added_item_count = 0
        self.logged_messages: list[str] = []
        self.qgis_iface = qgis_iface

        self._qgis_main_window: QObject | None = None
        self._qml_main_window: QObject | None = None
        self.qgis_map_canvas = qgis_iface.mapCanvas()

    @property
    def toast_messages(self) -> list[str]:
        toast_messages = self.qml_main_window.property("toastMessages")
        if hasattr(toast_messages, "toVariant"):
            return toast_messages.toVariant()
        return toast_messages

    @property
    def qml_main_window(self) -> QObject:
        if self._qml_main_window is None:
            raise ValueError("Add QML main window via set_main_window method first!")
        return self._qml_main_window

    def set_main_window(
        self, qgis_main_window: QObject, qml_main_window: QObject
    ) -> None:
        self._qgis_main_window = qgis_main_window
        self._qml_main_window = qml_main_window

    def show(self) -> None:
        if self._qgis_main_window is None:
            raise ValueError("Add mainWindow via set_main_window method first!")
        self._qgis_main_window.show()

    def set_qml_root(self, root: QObject) -> None:
        if not isinstance(root, QQuickItem):
            raise TypeError(f"Unsupported root type: {type(root)}")

        scene_root = self.qml_main_window.findChild(QObject, "host")
        if scene_root is None:
            raise RuntimeError("Could not find host item in main window")
        if not isinstance(scene_root, QQuickItem):
            raise TypeError(f"Host is not a QQuickItem: {type(scene_root)}")

        root.setParentItem(scene_root)
        root.setSize(scene_root.size())

    @pyqtSlot(result=QObject)
    def mainWindow(self) -> QObject:
        return self.qml_main_window

    @pyqtSlot(result=QObject)
    def mapCanvas(self) -> QObject:
        # host_item = self.qml_main_window.findChild(QObject, "host")
        # if host_item is not None:
        #     return host_item
        # if self.qgis_map_canvas is not None:
        #     return self.qgis_map_canvas
        return self.qml_main_window

    @pyqtSlot(QObject)
    def addItemToPluginsToolbar(self, _item: "QQuickItem") -> None:
        toolbar_row = self.qml_main_window.findChild(QObject, "pluginsToolbarRow")
        if toolbar_row is None:
            raise RuntimeError("Plugins toolbar row not found")
        _item.setSize(QSizeF(48, 48))
        _item.setParentItem(toolbar_row)

    @pyqtSlot(str)
    @pyqtSlot(str, str)
    @pyqtSlot(str, str, str)
    @pyqtSlot(str, str, str, str)
    @pyqtSlot(str, str, str, str, str)
    @pyqtSlot(str, str, str, str, str, str)
    @pyqtSlot(str, str, str, str, str, str, str)
    @pyqtSlot(str, str, str, str, str, str, str, str)
    @pyqtSlot(str, str, str, str, str, str, str, str, str)
    @pyqtSlot(str, str, str, str, str, str, str, str, str, str)
    def logMessage(self, *messages: str) -> None:
        self.logged_messages.extend(messages)


class QFieldPlatformUtilitiesStub(QObject):
    @pyqtSlot(result=bool)
    def isSystemDarkTheme(self) -> bool:
        return False


class QFieldStringUtilsStub(QObject):
    """
    String utilities stub.

    https://api.qfield.org/QField/classStringUtils/
    """

    @pyqtSlot(result=str)
    def createUuid(self) -> str:
        return f"{{{uuid.uuid4()}}}"
