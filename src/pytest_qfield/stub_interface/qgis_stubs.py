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

from PyQt6.QtCore import QObject, QSettings, QVariant, pyqtProperty, pyqtSlot


class QgsVectorLayerStub(QObject):
    """
    Stub implementation of QgsVectorLayer.
    """

    def __init__(self, layer_name: str, is_valid: bool) -> None:
        super().__init__()
        self._layer_name = layer_name
        self._is_valid = is_valid

    @pyqtProperty(str)
    def name(self) -> str:
        return self._layer_name

    @pyqtProperty(bool)
    def isValid(self) -> bool:
        # For some reason isValid is not a function,
        # but an attribute (or a property in python)
        return self._is_valid


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


class QSettingsStub(QSettings):
    @pyqtSlot(str, result="QVariant")
    @pyqtSlot(str, "QVariant", result="QVariant")
    def value(self, key: str, default_value: Any = None) -> "QVariant":  # noqa: ANN401
        return super().value(key, default_value)
