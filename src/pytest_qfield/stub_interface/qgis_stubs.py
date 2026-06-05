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
"""
Stub implementations of the QGIS classes QField exposes to QML.

Slots and properties that hand fresh ``QObject`` subclasses to QML must pin
``CppOwnership`` and append the stub to a ``_pinned_*_stubs`` list on the
parent. Without both, QML's JS engine may ``deleteLater`` the C++ object or
Python may GC the wrapper; the next slot handed the bare ``QObject`` back
then rebuilds a plain wrapper without the Python attributes (e.g.
``qgis_layer``) and crashes on first access.
"""

from typing import TYPE_CHECKING, Any, cast

from PyQt6.QtCore import (
    QObject,
    QSettings,
    QVariant,
    pyqtProperty,
    pyqtSignal,
    pyqtSlot,
)
from PyQt6.QtQml import QQmlEngine
from qgis.core import QgsRasterLayer, QgsVectorLayer

if TYPE_CHECKING:
    from qgis.core import QgsFeature, QgsGeometry, QgsMapLayer, QgsProject


class QgsMapLayerStub(QObject):
    """
    Stub implementation of QgsMapLayer.
    """

    def __init__(self, qgis_layer: "QgsMapLayer") -> None:
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

    @staticmethod
    def create_from_qgs_map_layer(map_layer: "QgsMapLayer") -> "QgsMapLayerStub":
        if isinstance(map_layer, QgsVectorLayer):
            return QgsVectorLayerStub(map_layer)
        if isinstance(map_layer, QgsRasterLayer):
            return QgsRasterLayerStub(map_layer)
        raise NotImplementedError


class QgsVectorLayerStub(QgsMapLayerStub):
    """
    Stub implementation of QgsVectorLayer.
    """

    featureAdded = pyqtSignal(int)
    featureDeleted = pyqtSignal(int)
    geometryChanged = pyqtSignal(int, object)
    afterCommitChanges = pyqtSignal()

    def __init__(self, qgis_layer: "QgsVectorLayer") -> None:
        super().__init__(qgis_layer)
        self.qgis_layer: QgsVectorLayer = cast("QgsVectorLayer", self.qgis_layer)
        self.qgis_layer.featureAdded.connect(self.featureAdded.emit)
        self.qgis_layer.featureDeleted.connect(self.featureDeleted.emit)
        self.qgis_layer.geometryChanged.connect(self.geometryChanged.emit)
        self.qgis_layer.afterCommitChanges.connect(self.afterCommitChanges.emit)
        self._pinned_feature_stubs: list[QgsFeatureStub] = []

    @pyqtSlot(result=bool)
    def startEditing(self) -> bool:
        return self.qgis_layer.startEditing()

    @pyqtSlot(result=bool)
    def commitChanges(self) -> bool:
        # TODO: stop editing or not?
        return self.qgis_layer.commitChanges(stopEditing=False)

    @pyqtSlot(int, result=QObject)
    def getFeature(self, feature_id: int) -> "QgsFeatureStub":
        stub = QgsFeatureStub(self.qgis_layer.getFeature(feature_id))
        stub.setParent(self)
        QQmlEngine.setObjectOwnership(stub, QQmlEngine.ObjectOwnership.CppOwnership)
        self._pinned_feature_stubs.append(stub)
        return stub


class QgsRasterLayerStub(QgsMapLayerStub):
    """
    Stub implementation of QgsRasterLayer.
    """

    featureAdded = pyqtSignal(int)

    def __init__(self, qgis_layer: "QgsRasterLayer") -> None:
        super().__init__(qgis_layer)
        self.qgis_layer: QgsRasterLayer = cast("QgsRasterLayer", self.qgis_layer)


class QgsProjectStub(QObject):
    """
    Stub implementation for QgsProject (qgisProject in QML).
    """

    def __init__(self, qgis_project: "QgsProject") -> None:
        super().__init__(parent=qgis_project)
        self.qgis_project = qgis_project
        self._pinned_layer_stubs: list[QgsMapLayerStub] = []

    @pyqtSlot(str, result=list)
    def mapLayersByName(self, name: str) -> list[QgsMapLayerStub]:
        stubs = [
            QgsMapLayerStub.create_from_qgs_map_layer(layer)
            for layer in self.qgis_project.mapLayersByName(name)
        ]
        for stub in stubs:
            QQmlEngine.setObjectOwnership(stub, QQmlEngine.ObjectOwnership.CppOwnership)
        self._pinned_layer_stubs.extend(stubs)
        return stubs


class QSettingsStub(QSettings):
    @pyqtSlot(str, result="QVariant")
    @pyqtSlot(str, "QVariant", result="QVariant")
    def value(self, key: str, default_value: Any = None) -> "QVariant":  # noqa: ANN401
        return super().value(key, default_value)

    @pyqtSlot(str, "QVariant")
    def setValue(self, key: str, value: Any) -> None:  # noqa: ANN401
        # QGS202 misfires here: it matches the method name and assumes the
        # raster setValue() success flag; QSettings.setValue returns void.
        super().setValue(key, value)  # noqa: QGS202

    @pyqtSlot(str)
    def remove(self, key: str) -> None:
        super().remove(key)


class QgsFeatureStub(QObject):
    def __init__(self, qgis_feature: "QgsFeature") -> None:
        super().__init__(parent=None)
        self.qgis_feature = qgis_feature
        self._pinned_geometry_stubs: list[QgsGeometryStub] = []

    @pyqtProperty(int)
    def id(self) -> int:
        return self.qgis_feature.id()

    @pyqtSlot(str, result="QVariant")
    def attribute(self, attribute_name: str) -> str | int | float | bool | None:
        return self.qgis_feature[attribute_name]

    @pyqtSlot(str, QVariant)
    def setAttribute(self, attribute_name: str, raw_value: QVariant | str) -> None:
        value = raw_value.value() if isinstance(raw_value, QVariant) else raw_value
        self.qgis_feature.setAttribute(
            self.qgis_feature.fieldNameIndex(attribute_name), value
        )

    @pyqtProperty(QObject)
    def geometry(self) -> "QgsGeometryStub":
        geometry_stub = QgsGeometryStub(self.qgis_feature.geometry())
        geometry_stub.setParent(self)
        QQmlEngine.setObjectOwnership(
            geometry_stub, QQmlEngine.ObjectOwnership.CppOwnership
        )
        self._pinned_geometry_stubs.append(geometry_stub)
        return geometry_stub


class QgsGeometryStub(QObject):
    def __init__(self, qgis_geometry: "QgsGeometry") -> None:
        super().__init__(parent=None)
        self.qgis_geometry = qgis_geometry

    @pyqtSlot(int, result=str)
    def asWkt(self, precision: int) -> str:
        return self.qgis_geometry.asWkt(precision)
