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
Stub implementations of QField's QML-facing classes.

See :mod:`pytest_qfield.stub_interface.qgis_stubs` for the
``CppOwnership`` pin + ``_pinned_*_stubs`` retention convention used by slots
and properties that return fresh ``QObject`` subclasses to QML.
"""

import uuid
from typing import TYPE_CHECKING, cast

from PyQt6.QtCore import QObject, QPointF, QSizeF, pyqtProperty, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtQml import QQmlEngine
from PyQt6.QtQuick import QQuickItem
from qgis.core import QgsFeatureRequest, QgsGeometry, QgsProject, QgsVectorLayerUtils

from pytest_qfield.stub_interface.qgis_stubs import (
    QgsFeatureStub,
    QgsGeometryStub,
    QgsVectorLayerStub,
)

if TYPE_CHECKING:
    from qgis.gui import QgisInterface, QgsMapCanvas


class QFieldAppInterfaceStub(QObject):
    """
    Stub implementation of AppInterface.

    https://api.qfield.org/QField/classAppInterface/
    """

    loadProjectEnded = pyqtSignal()

    def __init__(self, qgis_iface: "QgisInterface") -> None:
        super().__init__(parent=None)
        self.added_item_count = 0
        self.logged_messages: list[str] = []
        self.qgis_iface = qgis_iface

        self._qgis_main_window: QObject | None = None
        self._qml_main_window: QObject | None = None
        self.qgis_map_canvas = qgis_iface.mapCanvas()
        self.qml_map_canvas: QFieldMapCanvasStub = QFieldMapCanvasStub(
            qgis_map_canvas=self.qgis_map_canvas
        )
        self._named_items: dict[str, QObject] = {}

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
        return self.qml_map_canvas

    @pyqtSlot(QObject)
    def addItemToPluginsToolbar(self, _item: "QQuickItem") -> None:
        toolbar_row = self.qml_main_window.findChild(QObject, "pluginsToolbarRow")
        if toolbar_row is None:
            raise RuntimeError("Plugins toolbar row not found")
        _item.setSize(QSizeF(48, 48))
        _item.setParentItem(toolbar_row)

    def register_named_item(self, object_name: str, item: QObject) -> None:
        """
        Register a QObject so it can later be located via
        ``findItemByObjectName``.

        Mirrors how QField builds its item registry by ``objectName``. Tests
        usually do not call this directly; the ``pytest-qfield`` plugin
        auto-registers default stubs (e.g. ``positionSource``,
        ``geometryHighlighter``) for fixtures of the same name.
        """
        # findItemByObjectName returns a QObject through a pyqtSlot, which
        # flips the wrapper's ownership to JavaScriptOwnership. The next time
        # QML GCs that wrapper it would deleteLater() the underlying object
        # behind the Python ref held below — pin to C++ so Python stays the
        # sole authority over lifetime.
        QQmlEngine.setObjectOwnership(item, QQmlEngine.ObjectOwnership.CppOwnership)
        self._named_items[object_name] = item

    @pyqtSlot(str, result=QObject)
    def findItemByObjectName(self, name: str) -> QObject | None:
        """
        Stub implementation of ``AppInterface.findItemByObjectName``.

        https://api.qfield.org/QField/classAppInterface/

        Returns the QObject previously passed to
        :meth:`register_named_item`, or ``None`` if no such item is registered.
        """
        return self._named_items.get(name)

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

    # The readProject*Entry slots mirror AppInterface's QgsProject entry
    # readers, dropping the (value, ok) tuple QML cannot take. QField's C++
    # defaults the third argument, but plugin QML passes all three, so a
    # single full-signature slot per reader is enough.

    @pyqtSlot(str, str, str, result=str)
    def readProjectEntry(self, scope: str, key: str, default: str) -> str:
        value, _ = QgsProject.instance().readEntry(scope, key, default)
        return value

    @pyqtSlot(str, str, int, result=int)
    def readProjectNumEntry(self, scope: str, key: str, default: int) -> int:
        value, _ = QgsProject.instance().readNumEntry(scope, key, default)
        return value

    @pyqtSlot(str, str, float, result=float)
    def readProjectDoubleEntry(self, scope: str, key: str, default: float) -> float:
        value, _ = QgsProject.instance().readDoubleEntry(scope, key, default)
        return value

    @pyqtSlot(str, str, bool, result=bool)
    def readProjectBoolEntry(self, scope: str, key: str, default: bool) -> bool:
        value, _ = QgsProject.instance().readBoolEntry(scope, key, default)
        return value


class QFieldPlatformUtilitiesStub(QObject):
    @pyqtSlot(result=bool)
    def isSystemDarkTheme(self) -> bool:
        return False


class QFieldStringUtilsStub(QObject):
    """
    StringUtils stub.

    https://api.qfield.org/QField/classStringUtils/
    """

    @pyqtSlot(result=str)
    def createUuid(self) -> str:
        return f"{{{uuid.uuid4()}}}"


class QFieldGeometryUtilsStub(QObject):
    """
    GeometryUtils stub

    https://api.qfield.org/QField/classGeometryUtils/
    """

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent=parent)
        self._pinned_geometry_stubs: list[QgsGeometryStub] = []

    # TODO: add point method

    @pyqtSlot(str, result=QObject)
    def createGeometryFromWkt(self, wkt: str) -> QgsGeometryStub:
        geometry_stub = QgsGeometryStub(QgsGeometry.fromWkt(wkt))
        geometry_stub.setParent(self)
        QQmlEngine.setObjectOwnership(
            geometry_stub, QQmlEngine.ObjectOwnership.CppOwnership
        )
        self._pinned_geometry_stubs.append(geometry_stub)
        return geometry_stub


class QFieldLayerUtilsStub(QObject):
    """
    LayerUtils stub.

    https://api.qfield.org/QField/classLayerUtils
    """

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent=parent)
        self._pinned_iterator_stubs: list[FeatureIteratorStub] = []

    @pyqtSlot(QObject, QObject, result=bool)
    def addFeature(self, layer: QgsVectorLayerStub, feature: QgsFeatureStub) -> bool:
        return layer.qgis_layer.addFeature(feature.qgis_feature)

    @pyqtSlot(QObject, QObject, "qlonglong", result=bool)
    @pyqtSlot(QObject, QObject, "qlonglong", bool, result=bool)
    def deleteFeature(
        self,
        _project: QObject,
        layer: QgsVectorLayerStub,
        fid: int,
        flush_buffer: bool = True,
    ) -> bool:
        # The real LayerUtils::deleteFeature cascades to related features; the
        # stub just deletes ``fid``. It respects an already-open edit session:
        # only start editing when the layer wasn't editable, and only commit
        # when ``flushBuffer`` is set or we opened the session ourselves — so a
        # caller mid-edit keeps its uncommitted buffer. ``project`` is part of
        # the QField contract but isn't needed to exercise plugin delete paths.
        was_editing = layer.qgis_layer.isEditable()
        if not was_editing and not layer.qgis_layer.startEditing():
            return False
        deleted = layer.qgis_layer.deleteFeature(fid)
        if deleted and (flush_buffer or not was_editing):
            # QGS201 misfires once QgsProject is imported in this module — the
            # checker matches the bare method name, but this is a layer commit.
            layer.qgis_layer.commitChanges()  # noqa: QGS201, QGS202
        return deleted

    @pyqtSlot(QObject, str, result=QObject)
    def createFeatureIteratorFromExpression(
        self,
        layer: QgsVectorLayerStub,
        expression: str,
    ) -> "FeatureIteratorStub":
        iterator_stub = FeatureIteratorStub(
            layer, QgsFeatureRequest().setFilterExpression(expression)
        )
        iterator_stub.setParent(self)
        QQmlEngine.setObjectOwnership(
            iterator_stub, QQmlEngine.ObjectOwnership.CppOwnership
        )
        self._pinned_iterator_stubs.append(iterator_stub)
        return iterator_stub

    def get_iterators(self) -> list["FeatureIteratorStub"]:
        return self.findChildren(FeatureIteratorStub)

    def clear_iterators(self) -> None:
        for child in self.findChildren(FeatureIteratorStub):
            child.setParent(None)
            child.deleteLater()


class FeatureIteratorStub(QObject):
    """FeatureIterator stub."""

    def __init__(self, layer: QgsVectorLayerStub, request: QgsFeatureRequest) -> None:
        super().__init__(parent=None)
        self.layer = layer
        self.request = request
        self._features = list(layer.qgis_layer.getFeatures(self.request))
        self.iterated_count = 0
        self.closed = False
        self._pinned_feature_stubs: list[QgsFeatureStub] = []

    @pyqtSlot(result=bool)
    def hasNext(self) -> bool:
        return len(self._features) > 0 and self.iterated_count < len(self._features)

    @pyqtSlot(result=QObject)
    def next(self) -> QgsFeatureStub:
        feature_stub = QgsFeatureStub(self._features[self.iterated_count])
        feature_stub.setParent(self)
        QQmlEngine.setObjectOwnership(
            feature_stub, QQmlEngine.ObjectOwnership.CppOwnership
        )
        self._pinned_feature_stubs.append(feature_stub)
        self.iterated_count += 1
        return feature_stub

    @pyqtSlot()
    def close(self) -> None:
        self.closed = True


class QFieldProjectedPositionStub(QObject):
    """
    Stub for the QgsPoint returned by ``Positioning.projectedPosition``.
    """

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._x = x
        self._y = y

    @pyqtProperty(float, constant=True)
    def x(self) -> float:
        return self._x

    @pyqtProperty(float, constant=True)
    def y(self) -> float:
        return self._y


class QFieldPositioningStub(QObject):
    """
    Stub implementation for Positioning, the QML ``positionSource`` item.

    https://github.com/opengisch/QField/blob/master/src/core/positioning/positioning.h
    """

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        active: bool = True,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._projected_position = QFieldProjectedPositionStub(x, y, parent=self)
        self._active = active

    @pyqtProperty(QObject, constant=True)
    def projectedPosition(self) -> QFieldProjectedPositionStub:
        return self._projected_position

    @pyqtProperty(bool, constant=True)
    def active(self) -> bool:
        return self._active


class QFieldGeometryWrapperStub(QObject):
    """
    Stub implementation for GeometryWrapper.

    https://github.com/opengisch/QField/blob/master/src/core/utils/geometrywrapper.h
    """

    crsChanged = pyqtSignal()
    qgsGeometryChanged = pyqtSignal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent=parent)
        self._crs: object = None
        self._qgs_geometry: object = None

    @pyqtProperty("QVariant", notify=crsChanged)
    def crs(self) -> object:
        return self._crs

    @crs.setter  # type: ignore[no-redef]
    def crs(self, value: object) -> None:
        if self._crs == value:
            return
        self._crs = value
        self.crsChanged.emit()

    @pyqtProperty("QVariant", notify=qgsGeometryChanged)
    def qgsGeometry(self) -> object:
        return self._qgs_geometry

    @qgsGeometry.setter  # type: ignore[no-redef]
    def qgsGeometry(self, value: object) -> None:
        if self._qgs_geometry == value:
            return
        self._qgs_geometry = value
        self.qgsGeometryChanged.emit()

    @pyqtSlot()
    def clear(self) -> None:
        self.crs = None  # type: ignore[method-assign]
        self.qgsGeometry = None  # type: ignore[method-assign]


class QFieldGeometryHighlighterStub(QObject):
    """
    Stub implementation for GeometryHighlighter.

    https://github.com/opengisch/QField/blob/master/src/core/utils/geometryhighlighter.h
    """

    durationChanged = pyqtSignal()
    visibleChanged = pyqtSignal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent=parent)
        self._geometry_wrapper = QFieldGeometryWrapperStub(parent=self)
        self._duration = 0
        self._visible = False

    @pyqtProperty(QObject, constant=True)
    def geometryWrapper(self) -> QFieldGeometryWrapperStub:
        return self._geometry_wrapper

    @pyqtProperty(int, notify=durationChanged)
    def duration(self) -> int:
        return self._duration

    @duration.setter  # type: ignore[no-redef]
    def duration(self, value: int) -> None:
        if self._duration == value:
            return
        self._duration = int(value)
        self.durationChanged.emit()

    @pyqtProperty(bool, notify=visibleChanged)
    def visible(self) -> bool:
        return self._visible

    @visible.setter  # type: ignore[no-redef]
    def visible(self, value: bool) -> None:
        if self._visible == value:
            return
        self._visible = bool(value)
        self.visibleChanged.emit()

    @pyqtSlot()
    def update(self) -> None:
        pass


class QFieldMultiFeatureListModelStub(QObject):
    """
    Stub implementation of the ``model`` exposed by ``FeatureListForm``.

    https://github.com/opengisch/QField/blob/master/src/core/multifeaturelistmodel.h

    Only the ``setFeatures(layer, filter)`` slot is exercised — that's what
    QField's plugin-facing QML calls to navigate to a feature by attribute
    filter. Each call is appended to ``set_features_calls`` so tests can
    assert "was this called once with the right args?".
    """

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent=parent)
        self.set_features_calls: list[tuple[QObject, str]] = []

    @pyqtSlot(QObject, str)
    def setFeatures(self, layer: QObject, filter_expression: str) -> None:
        self.set_features_calls.append((layer, filter_expression))


class QFieldFeatureListModelSelectionStub(QObject):
    """
    Stub implementation of the ``selection`` exposed by ``FeatureListForm``.

    https://github.com/opengisch/QField/blob/master/src/core/featurelistmodelselection.h

    Exposes ``focusedItem`` as a settable index — plugins set it to ``0``
    after a single-row ``model.setFeatures`` to focus the matched feature.

    ``focusedFeature`` / ``focusedLayer`` resolve the feature and layer that
    ``focusedItem`` points at, reading from the model's most recent
    ``setFeatures(layer, filter)`` call: the layer is that call's layer, and the
    feature is the ``focusedItem``-th match of its filter expression. This is
    the exact flow a plugin uses to open a form
    (``model.setFeatures(layer, "id = '...'")`` + ``focusedItem = 0``), then
    reads ``selection.focusedFeature`` / ``focusedLayer`` from the handler. Both
    return ``None`` until a feature is focused.
    """

    focusedItemChanged = pyqtSignal()

    def __init__(
        self,
        model: "QFieldMultiFeatureListModelStub",
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._model = model
        self._focused_item = -1
        self._pinned_feature_stubs: list[QgsFeatureStub] = []

    @pyqtProperty(int, notify=focusedItemChanged)
    def focusedItem(self) -> int:
        return self._focused_item

    @focusedItem.setter  # type: ignore[no-redef]
    def focusedItem(self, value: int) -> None:
        if self._focused_item == value:
            return
        self._focused_item = int(value)
        self.focusedItemChanged.emit()

    @pyqtProperty(QObject)
    def focusedLayer(self) -> QgsVectorLayerStub | None:
        call = self._focused_setfeatures_call()
        return cast("QgsVectorLayerStub", call[0]) if call else None

    @pyqtProperty(QObject)
    def focusedFeature(self) -> QgsFeatureStub | None:
        call = self._focused_setfeatures_call()
        if call is None:
            return None
        layer = cast("QgsVectorLayerStub", call[0])
        request = QgsFeatureRequest().setFilterExpression(call[1])
        features = list(layer.qgis_layer.getFeatures(request))
        if self._focused_item >= len(features):
            return None
        stub = QgsFeatureStub(features[self._focused_item])
        stub.setParent(self)
        QQmlEngine.setObjectOwnership(stub, QQmlEngine.ObjectOwnership.CppOwnership)
        self._pinned_feature_stubs.append(stub)
        return stub

    def _focused_setfeatures_call(self) -> tuple[QObject, str] | None:
        if self._focused_item < 0 or not self._model.set_features_calls:
            return None
        return self._model.set_features_calls[-1]


class QFieldFeatureListFormStub(QObject):
    """
    Stub implementation for ``FeatureListForm`` (objectName ``"featureForm"``).

    https://github.com/opengisch/QField/blob/master/src/qml/FeatureListForm.qml

    The QML id is ``featureListForm`` but the ``objectName`` is ``featureForm``
    — that's the name plugins pass to ``iface.findItemByObjectName``. Plugins
    drive an existing-feature attribute form via this surface::

        const form = iface.findItemByObjectName("featureForm");
        form.model.setFeatures(layer, "id = '" + uuid + "'");
        form.selection.focusedItem = 0;
        form.state = "FeatureFormEdit";

    ``overlayFeatureFormDrawer`` is a separate (post-digitize) item — see
    :class:`QFieldOverlayFeatureFormDrawerStub`; don't confuse the two.

    ``visible`` mirrors ``props.isVisible`` (``visible: props.isVisible`` in
    QField): it is ``true`` whenever a feature is shown, in either the
    read-only ``"FeatureForm"`` view or the ``"FeatureFormEdit"`` edit state.
    Plugins that hide overlays while a form covers the map watch it.
    """

    stateChanged = pyqtSignal()
    visibleChanged = pyqtSignal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent=parent)
        self._model = QFieldMultiFeatureListModelStub(parent=self)
        self._selection = QFieldFeatureListModelSelectionStub(self._model, parent=self)
        self._state = ""
        self._visible = False

    @pyqtProperty(QObject, constant=True)
    def model(self) -> QFieldMultiFeatureListModelStub:
        return self._model

    @pyqtProperty(QObject, constant=True)
    def selection(self) -> QFieldFeatureListModelSelectionStub:
        return self._selection

    @pyqtProperty(str, notify=stateChanged)
    def state(self) -> str:
        return self._state

    @state.setter  # type: ignore[no-redef]
    def state(self, value: str) -> None:
        if self._state == value:
            return
        self._state = str(value)
        self.stateChanged.emit()

    @pyqtProperty(bool, notify=visibleChanged)
    def visible(self) -> bool:
        return self._visible

    @visible.setter  # type: ignore[no-redef]
    def visible(self, value: bool) -> None:
        if self._visible == value:
            return
        self._visible = bool(value)
        self.visibleChanged.emit()


class QFieldOverlayFeatureFormDrawerStub(QObject):
    """
    Stub implementation for ``overlayFeatureFormDrawer``.

    https://github.com/opengisch/QField/blob/master/src/qml/qgismobileapp.qml

    The drawer that slides in over the map after digitizing a feature. Distinct
    from ``featureForm`` (:class:`QFieldFeatureListFormStub`), which is the
    identify/attribute panel. Plugins read ``opened`` to tell whether the
    drawer currently covers the map (QField's own ``mapCanvas.isEnabled``
    checks ``!overlayFeatureFormDrawer.opened`` the same way).

    ``shown_features`` records the ``(layer, feature_id)`` pairs the drawer has
    been opened for — the drawer has no QML ``model`` surface of its own, so
    this Python-side log is how tests assert which feature was shown (mirroring
    ``QFieldMultiFeatureListModelStub.set_features_calls``).
    """

    openedChanged = pyqtSignal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent=parent)
        self._opened = False
        self.shown_features: list[tuple[QObject, int]] = []

    @pyqtProperty(bool, notify=openedChanged)
    def opened(self) -> bool:
        return self._opened

    @opened.setter  # type: ignore[no-redef]
    def opened(self, value: bool) -> None:
        if self._opened == value:
            return
        self._opened = bool(value)
        self.openedChanged.emit()


class QFieldMapSettingsStub(QObject):
    """
    Stub implementation for ``MapCanvas.mapSettings`` (a subset of MapSettings).

    https://github.com/opengisch/QField/blob/master/src/core/mapsettings.h
    """

    def __init__(
        self,
        qgis_map_canvas: "QgsMapCanvas | None" = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._qgis_map_canvas = qgis_map_canvas

    @pyqtSlot(QPointF, result=QPointF)
    def screenToCoordinate(self, point: QPointF) -> QPointF:
        if self._qgis_map_canvas is None:
            return point
        map_to_pixel = self._qgis_map_canvas.mapSettings().mapToPixel()
        coord = map_to_pixel.toMapCoordinatesF(point.x(), point.y())
        return QPointF(coord.x(), coord.y())


class QFieldMapCanvasStub(QObject):
    """
    Stub implementation for the QML ``MapCanvas`` item returned by
    ``iface.mapCanvas()``.

    https://github.com/opengisch/QField/blob/master/src/qml/MapCanvas.qml
    """

    clicked = pyqtSignal(QPointF, int)
    confirmedClicked = pyqtSignal(QPointF, int)

    def __init__(
        self,
        qgis_map_canvas: "QgsMapCanvas | None" = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._map_settings = QFieldMapSettingsStub(
            qgis_map_canvas=qgis_map_canvas, parent=self
        )

    @pyqtProperty(QObject, constant=True)
    def mapSettings(self) -> QFieldMapSettingsStub:
        return self._map_settings


class QFieldFeatureUtilsStub(QObject):
    """FeatureUtils stub.

    https://api.qfield.org/QField/classFeatureUtils/
    """

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent=parent)
        self._pinned_feature_stubs: list[QgsFeatureStub] = []

    @pyqtSlot(QObject, result=QObject)
    @pyqtSlot(QObject, QObject, result=QObject)
    def createFeature(
        self, layer: QgsVectorLayerStub, geometry: QgsGeometryStub | None = None
    ) -> QgsFeatureStub:
        feature = QgsVectorLayerUtils.createFeature(
            layer.qgis_layer,
            geometry=geometry.qgis_geometry if geometry else QgsGeometry(),
        )
        stub = QgsFeatureStub(feature)
        stub.setParent(self)
        QQmlEngine.setObjectOwnership(stub, QQmlEngine.ObjectOwnership.CppOwnership)
        self._pinned_feature_stubs.append(stub)
        return stub


class QFieldThemeStub(QObject):
    """
    Stub implementation of Theme.

    Provides color, font, and layout properties used throughout
    QField's QML components. In newer QField versions (>v4.0.6),
    Theme is a C++ singleton rather than a QML-only module.

    https://github.com/opengisch/QField/blob/master/src/core/theme.h
    """

    themeDataLoaded = pyqtSignal()
    darkThemeChanged = pyqtSignal()
    fontScaleChanged = pyqtSignal()

    _PPI_XXXHDPI = 360
    _PPI_XXHDPI = 270
    _PPI_XHDPI = 180
    _PPI_HDPI = 135

    def __init__(
        self,
        system_font_point_size: float = 14.0,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._systemFontPointSize = system_font_point_size
        self._fontScale = 1.0
        self._darkTheme = False
        self._screenPpi = 160.0
        self._init_theme_colors()
        self._init_fixed_colors()

    def _init_theme_colors(self) -> None:
        self._mainColor = QColor("#80cc28")
        self._mainOverlayColor = QColor("#ffffff")
        self._mainBackgroundColor = QColor("#ffffff")
        self._mainBackgroundColorSemiOpaque = QColor(255, 255, 255, 187)
        self._mainTextColor = QColor("#000000")
        self._mainTextDisabledColor = QColor("#888888")
        self._secondaryTextColor = QColor("#555555")
        self._controlBackgroundColor = QColor("#f0f0f0")
        self._controlBackgroundAlternateColor = QColor("#e8e8e8")
        self._controlBackgroundDisabledColor = QColor("#d0d0d0")
        self._controlBorderColor = QColor("#cccccc")
        self._buttonColor = QColor("#ffffff")
        self._buttonBackgroundColor = QColor("#80cc28")
        self._toolButtonColor = QColor("#000000")
        self._toolButtonBackgroundColor = QColor("#ffffff")
        self._toolButtonBackgroundSemiOpaqueColor = QColor(255, 255, 255, 187)
        self._scrollBarBackgroundColor = QColor("#cccccc")
        self._groupBoxBackgroundColor = QColor("#ffffff")
        self._groupBoxSurfaceColor = QColor("#f5f5f5")
        self._goodColor = QColor("#80cc28")
        self._warningColor = QColor("#fd9626")
        self._errorColor = QColor("#c0392b")

    def _init_fixed_colors(self) -> None:
        self._mainColorSemiOpaque = QColor(128, 204, 40, 187)
        self._darkRed = QColor("#c0392b")
        self._darkGray = QColor("#555555")
        self._darkGraySemiOpaque = QColor(85, 85, 85, 187)
        self._gray = QColor("#888888")
        self._lightGray = QColor("#cccccc")
        self._lightestGray = QColor("#e8e8e8")
        self._lightestGraySemiOpaque = QColor(232, 232, 232, 187)
        self._light = QColor("#f0f0f0")
        self._cloudColor = QColor("#4c6daa")
        self._positionColor = QColor("#64b5f6")
        self._positionColorSemiOpaque = QColor(100, 181, 246, 187)
        self._positionBackgroundColor = QColor("#3d7bc4")
        self._darkPositionColor = QColor("#2a5c99")
        self._darkPositionColorSemiOpaque = QColor(42, 92, 153, 187)
        self._accuracyBad = QColor("#c0392b")
        self._accuracyTolerated = QColor("#fd9626")
        self._accuracyExcellent = QColor("#80cc28")
        self._navigationColor = QColor("#984ea3")
        self._navigationColorSemiOpaque = QColor(152, 78, 163, 187)
        self._navigationBackgroundColor = QColor("#6b3571")
        self._sensorBackgroundColor = QColor("#e67e22")
        self._bookmarkDefault = QColor("#80cc28")
        self._bookmarkOrange = QColor("#fd9626")
        self._bookmarkRed = QColor("#c0392b")
        self._bookmarkBlue = QColor("#4c6daa")
        self._qfieldcloudBlue = QColor("#4c6daa")
        self._vertexColor = QColor("#e74c3c")
        self._vertexColorSemiOpaque = QColor(231, 76, 60, 187)
        self._vertexSelectedColor = QColor("#3498db")
        self._vertexSelectedColorSemiOpaque = QColor(52, 152, 219, 187)
        self._vertexNewColor = QColor("#2ecc71")
        self._vertexNewColorSemiOpaque = QColor(46, 204, 113, 187)
        self._processingPreview = QColor("#ff00ff")

    # Color properties (all notify via themeDataLoaded for simplicity)
    @pyqtProperty(QColor, notify=themeDataLoaded)
    def mainColor(self) -> QColor:
        return self._mainColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def mainOverlayColor(self) -> QColor:
        return self._mainOverlayColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def mainBackgroundColor(self) -> QColor:
        return self._mainBackgroundColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def mainBackgroundColorSemiOpaque(self) -> QColor:
        return self._mainBackgroundColorSemiOpaque

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def mainTextColor(self) -> QColor:
        return self._mainTextColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def mainTextDisabledColor(self) -> QColor:
        return self._mainTextDisabledColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def secondaryTextColor(self) -> QColor:
        return self._secondaryTextColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def controlBackgroundColor(self) -> QColor:
        return self._controlBackgroundColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def controlBackgroundAlternateColor(self) -> QColor:
        return self._controlBackgroundAlternateColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def controlBackgroundDisabledColor(self) -> QColor:
        return self._controlBackgroundDisabledColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def controlBorderColor(self) -> QColor:
        return self._controlBorderColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def buttonColor(self) -> QColor:
        return self._buttonColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def buttonBackgroundColor(self) -> QColor:
        return self._buttonBackgroundColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def toolButtonColor(self) -> QColor:
        return self._toolButtonColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def toolButtonBackgroundColor(self) -> QColor:
        return self._toolButtonBackgroundColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def toolButtonBackgroundSemiOpaqueColor(self) -> QColor:
        return self._toolButtonBackgroundSemiOpaqueColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def scrollBarBackgroundColor(self) -> QColor:
        return self._scrollBarBackgroundColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def groupBoxBackgroundColor(self) -> QColor:
        return self._groupBoxBackgroundColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def groupBoxSurfaceColor(self) -> QColor:
        return self._groupBoxSurfaceColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def goodColor(self) -> QColor:
        return self._goodColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def warningColor(self) -> QColor:
        return self._warningColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def errorColor(self) -> QColor:
        return self._errorColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def mainColorSemiOpaque(self) -> QColor:
        return self._mainColorSemiOpaque

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def darkRed(self) -> QColor:
        return self._darkRed

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def darkGray(self) -> QColor:
        return self._darkGray

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def darkGraySemiOpaque(self) -> QColor:
        return self._darkGraySemiOpaque

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def gray(self) -> QColor:
        return self._gray

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def lightGray(self) -> QColor:
        return self._lightGray

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def lightestGray(self) -> QColor:
        return self._lightestGray

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def lightestGraySemiOpaque(self) -> QColor:
        return self._lightestGraySemiOpaque

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def light(self) -> QColor:
        return self._light

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def cloudColor(self) -> QColor:
        return self._cloudColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def positionColor(self) -> QColor:
        return self._positionColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def positionColorSemiOpaque(self) -> QColor:
        return self._positionColorSemiOpaque

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def positionBackgroundColor(self) -> QColor:
        return self._positionBackgroundColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def darkPositionColor(self) -> QColor:
        return self._darkPositionColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def darkPositionColorSemiOpaque(self) -> QColor:
        return self._darkPositionColorSemiOpaque

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def accuracyBad(self) -> QColor:
        return self._accuracyBad

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def accuracyTolerated(self) -> QColor:
        return self._accuracyTolerated

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def accuracyExcellent(self) -> QColor:
        return self._accuracyExcellent

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def navigationColor(self) -> QColor:
        return self._navigationColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def navigationColorSemiOpaque(self) -> QColor:
        return self._navigationColorSemiOpaque

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def navigationBackgroundColor(self) -> QColor:
        return self._navigationBackgroundColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def sensorBackgroundColor(self) -> QColor:
        return self._sensorBackgroundColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def bookmarkDefault(self) -> QColor:
        return self._bookmarkDefault

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def bookmarkOrange(self) -> QColor:
        return self._bookmarkOrange

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def bookmarkRed(self) -> QColor:
        return self._bookmarkRed

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def bookmarkBlue(self) -> QColor:
        return self._bookmarkBlue

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def qfieldcloudBlue(self) -> QColor:
        return self._qfieldcloudBlue

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def vertexColor(self) -> QColor:
        return self._vertexColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def vertexColorSemiOpaque(self) -> QColor:
        return self._vertexColorSemiOpaque

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def vertexSelectedColor(self) -> QColor:
        return self._vertexSelectedColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def vertexSelectedColorSemiOpaque(self) -> QColor:
        return self._vertexSelectedColorSemiOpaque

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def vertexNewColor(self) -> QColor:
        return self._vertexNewColor

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def vertexNewColorSemiOpaque(self) -> QColor:
        return self._vertexNewColorSemiOpaque

    @pyqtProperty(QColor, notify=themeDataLoaded)
    def processingPreview(self) -> QColor:
        return self._processingPreview

    def _make_font(self, scale_factor: float, bold: bool) -> QFont:
        font = QFont()
        font.setPointSizeF(self._systemFontPointSize * self._fontScale * scale_factor)
        font.setBold(bold)
        font.setWeight(QFont.Weight.Bold if bold else QFont.Weight.Normal)
        return font

    # Bool / scalar properties
    @pyqtProperty(bool, notify=darkThemeChanged)
    def darkTheme(self) -> bool:
        return self._darkTheme

    @pyqtProperty(float, notify=fontScaleChanged)
    def fontScale(self) -> float:
        return self._fontScale

    # Font properties
    @pyqtProperty(QFont, notify=fontScaleChanged)
    def defaultFont(self) -> QFont:
        return self._make_font(1.0, bold=False)

    @pyqtProperty(QFont, notify=fontScaleChanged)
    def tinyFont(self) -> QFont:
        return self._make_font(0.75, bold=False)

    @pyqtProperty(QFont, notify=fontScaleChanged)
    def tipFont(self) -> QFont:
        return self._make_font(0.875, bold=False)

    @pyqtProperty(QFont, notify=fontScaleChanged)
    def resultFont(self) -> QFont:
        return self._make_font(0.8125, bold=False)

    @pyqtProperty(QFont, notify=fontScaleChanged)
    def strongFont(self) -> QFont:
        return self._make_font(1.0, bold=True)

    @pyqtProperty(QFont, notify=fontScaleChanged)
    def strongTipFont(self) -> QFont:
        return self._make_font(0.875, bold=True)

    @pyqtProperty(QFont, notify=fontScaleChanged)
    def secondaryTitleFont(self) -> QFont:
        return self._make_font(1.125, bold=False)

    @pyqtProperty(QFont, notify=fontScaleChanged)
    def titleFont(self) -> QFont:
        return self._make_font(1.25, bold=False)

    @pyqtProperty(QFont, notify=fontScaleChanged)
    def strongTitleFont(self) -> QFont:
        return self._make_font(1.25, bold=True)

    # Layout constants
    @pyqtProperty(int, constant=True)
    def popupScreenEdgeVerticalMargin(self) -> int:
        return 40

    @pyqtProperty(int, constant=True)
    def popupScreenEdgeHorizontalMargin(self) -> int:
        return 20

    @pyqtProperty(int, constant=True)
    def menuItemIconlessLeftPadding(self) -> int:
        return 52

    @pyqtProperty(int, constant=True)
    def menuItemLeftPadding(self) -> int:
        return 12

    @pyqtProperty(int, constant=True)
    def menuItemCheckLeftPadding(self) -> int:
        return 16

    # Invokable methods
    @pyqtSlot(str, result=str)
    def getThemeIcon(self, name: str) -> str:
        if self._screenPpi >= self._PPI_XXXHDPI:
            density = "xxxhdpi"
        elif self._screenPpi >= self._PPI_XXHDPI:
            density = "xxhdpi"
        elif self._screenPpi >= self._PPI_XHDPI:
            density = "xhdpi"
        elif self._screenPpi >= self._PPI_HDPI:
            density = "hdpi"
        else:
            density = "mdpi"
        return f"qrc:/themes/qfield/{density}/{name}.png"

    @pyqtSlot(str, result=str)
    def getThemeVectorIcon(self, name: str) -> str:
        return f"qrc:/themes/qfield/nodpi/{name}.svg"

    @pyqtSlot(QColor, result=str)
    def colorToHtml(self, color: QColor) -> str:
        return (
            f"rgba({int(color.redF() * 255)},"
            f"{int(color.greenF() * 255)},"
            f"{int(color.blueF() * 255)},"
            f"{int(color.alphaF() * 255)})"
        )
