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

from typing import TYPE_CHECKING, Any

from PyQt6.QtCore import QObject, QSettings, QVariant, pyqtProperty, pyqtSlot

if TYPE_CHECKING:
    from qgis.core import QgsProject, QgsVectorLayer


class QgsVectorLayerStub(QObject):
    """
    Stub implementation of QgsVectorLayer.
    """

    def __init__(self, qgis_layer: "QgsVectorLayer") -> None:
        super().__init__(parent=qgis_layer)
        self.qgis_layer = qgis_layer

    @pyqtProperty(str)
    def name(self) -> str:
        return self.qgis_layer.name()

    @pyqtProperty(bool)
    def isValid(self) -> bool:
        # For some reason isValid is not a function,
        # but an attribute (or a property in python)
        return self.qgis_layer.isValid()


class QgsProjectStub(QObject):
    """
    Stub implementation for QgsProject (qgisProject in QML).
    """

    def __init__(self, qgis_project: "QgsProject") -> None:
        super().__init__(parent=qgis_project)
        self.qgis_project = qgis_project

    @pyqtSlot(str, result=list)
    def mapLayersByName(self, name: str) -> list[QgsVectorLayerStub]:
        return list(map(QgsVectorLayerStub, self.qgis_project.mapLayersByName(name)))


class QSettingsStub(QSettings):
    @pyqtSlot(str, result="QVariant")
    @pyqtSlot(str, "QVariant", result="QVariant")
    def value(self, key: str, default_value: Any = None) -> "QVariant":  # noqa: ANN401
        return super().value(key, default_value)
