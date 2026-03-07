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

from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtQuick import QQuickItem, QQuickWindow
from PyQt6.QtWidgets import QMainWindow, QToolBar, QWidget


class QFieldAppInterfaceStub(QObject):
    def __init__(self) -> None:
        super().__init__()
        self.added_item_count = 0
        self.logged_messages: list[str] = []

        self._main_window = QMainWindow()
        self._main_window.setWindowTitle("Test window")

        self._toolbar = self._main_window.addToolBar("Plugin toolbar")

        self._quick_window = QQuickWindow()
        self._qml_container = QWidget.createWindowContainer(
            self._quick_window, self._main_window
        )
        self._main_window.setCentralWidget(self._qml_container)

    def show(self) -> None:
        self._main_window.show()

    def set_qml_root(self, root: QObject) -> None:
        if isinstance(root, QQuickItem):
            scene_root = self._quick_window.contentItem()
            root.setParentItem(scene_root)
            root.setSize(scene_root.size())
        else:
            raise TypeError(f"Unsupported root type: {type(root)}")

    @property
    def plugin_toolbar(self) -> "QToolBar":
        return self._toolbar

    @pyqtSlot(result=QObject)
    def mainWindow(self) -> QObject:
        return self._quick_window.contentItem()

    @pyqtSlot(result=QObject)
    def mapCanvas(self) -> QObject:
        # Return a QQuickItem to be used as a QML parent
        return self.mainWindow()

    @pyqtSlot(QObject)
    def addItemToPluginsToolbar(self, _item: QQuickItem) -> None:
        quick_window = QQuickWindow()
        _item.setParentItem(quick_window.contentItem())
        container = QWidget.createWindowContainer(quick_window)
        container.setMinimumSize(int(_item.width()), int(_item.height()))
        container.setMaximumSize(int(_item.width()), int(_item.height()))
        self._toolbar.addWidget(container)

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
