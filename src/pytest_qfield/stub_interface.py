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
from typing import Any

from PyQt6.QtCore import QObject, QSettings, QSizeF, QVariant, pyqtSlot
from PyQt6.QtQuick import QQuickItem, QQuickWindow


class QFieldAppInterfaceStub(QObject):
    def __init__(self) -> None:
        super().__init__()
        self.added_item_count = 0
        self.logged_messages: list[str] = []

        self._main_window: QQuickWindow | None = None

    @property
    def toast_messages(self) -> list[str]:
        return self.mainWindow().property("toastMessages").toVariant()

    def set_main_window(self, main_window: "QQuickWindow") -> None:
        self._main_window = main_window

    def show(self) -> None:
        self.mainWindow().show()

    def set_qml_root(self, root: QObject) -> None:
        if not isinstance(root, QQuickItem):
            raise TypeError(f"Unsupported root type: {type(root)}")

        scene_root = self.mainWindow().findChild(QObject, "host")
        if scene_root is None:
            raise RuntimeError("Could not find host item in main window")
        if not isinstance(scene_root, QQuickItem):
            raise TypeError(f"Host is not a QQuickItem: {type(scene_root)}")

        root.setParentItem(scene_root)
        root.setSize(scene_root.size())

    @pyqtSlot(result=QObject)
    def mainWindow(self) -> "QQuickWindow":
        if self._main_window is None:
            raise ValueError("Add mainWindow via set_main_window method first!")
        return self._main_window

    @pyqtSlot(result=QObject)
    def mapCanvas(self) -> QObject:
        # Return a QQuickItem to be used as a QML parent
        return self.mainWindow()

    @pyqtSlot(QObject)
    def addItemToPluginsToolbar(self, _item: "QQuickItem") -> None:
        toolbar_row = self.mainWindow().findChild(QObject, "pluginsToolbarRow")
        if toolbar_row is None:
            raise RuntimeError("Plugins toolbar row not found")
        _item.setSize(QSizeF(48, 48))
        _item.setParentItem(toolbar_row)

    @pyqtSlot(str)
    def logMessage(self, message: str) -> None:
        self.logged_messages.append(message)


class QgsProjectStub(QObject):
    """
    Stub implementation for QgsProject (qgisProject in QML).
    """

    def __init__(self) -> None:
        super().__init__()
        self.map_layers: dict[str, Any] = {}

    @pyqtSlot(str, result=list)
    def mapLayersByName(self, name: str) -> list:
        if name not in self.map_layers:
            return []
        return [self.map_layers[name]]


class QFieldPlatformUtilitiesStub(QObject):
    @pyqtSlot(result=bool)
    def isSystemDarkTheme(self) -> bool:
        return False


class QSettingsStub(QSettings):
    @pyqtSlot(str, result="QVariant")
    @pyqtSlot(str, "QVariant", result="QVariant")
    def value(self, key: str, default_value: Any = None) -> "QVariant":  # noqa: ANN401
        return super().value(key, default_value)
