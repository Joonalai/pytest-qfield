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

from typing import TYPE_CHECKING

import pytest
from PyQt6.QtQml import QQmlEngine

from pytest_qfield.stub_interface.qfield_stubs import (
    QFieldFeatureListFormStub,
    QFieldPositioningStub,
)

if TYPE_CHECKING:
    from pathlib import Path

    from qgis.core import QgsVectorLayer

    from pytest_qfield.qfieldbot import QFieldBot
    from pytest_qfield.stub_interface.qfield_stubs import (
        QFieldGeometryHighlighterStub,
    )
    from pytest_qfield.stub_interface.qgis_stubs import QgsProjectStub


@pytest.fixture
def qfield_positioning_stub() -> QFieldPositioningStub:
    """Return a Positioning stub anchored at fixed test coordinates."""
    return QFieldPositioningStub(x=389870.0, y=6678167.0, active=True)


@pytest.fixture
def load_stub_plugin(
    qfield_bot: "QFieldBot",
    data_path: "Path",
    layer_points: "QgsVectorLayer",
    qgs_project_stub: "QgsProjectStub",
):
    qfield_bot.show_window()
    qfield_bot.load_plugin(
        data_path / "stub_tester_plugin" / "main.qml",
        raise_if_warnings=True,
        emit_load_project_ended=False,
    )
    assert qgs_project_stub.qgis_project.addMapLayer(layer_points)
    qfield_bot.iface.qgis_map_canvas.setExtent(layer_points.extent())
    qfield_bot.emit_load_project_ended()
    qfield_bot.iface.logged_messages.clear()


@pytest.mark.usefixtures("load_stub_plugin")
def test_position_source_can_be_overridden_via_fixture(qfield_bot: "QFieldBot"):
    qfield_bot.click_item(qfield_bot.get_item("test_position_source"))
    assert qfield_bot.iface.logged_messages == [
        "positionSource active: true",
        "positionSource x: 389870",
        "positionSource y: 6678167",
    ]


def test_named_item_lookup_does_not_transfer_ownership_to_qml(
    qfield_bot: "QFieldBot",
    tmp_path: "Path",
    qfield_geometry_highlighter_stub: "QFieldGeometryHighlighterStub",
):
    """
    Reaching the highlighter through ``iface.findItemByObjectName`` must leave
    its ownership as ``CppOwnership``. JavaScriptOwnership would let the QML
    engine ``deleteLater()`` the underlying C++ object behind Python's back the
    next time the JS wrapper is collected, which would dangle the Python ref
    held in ``iface._named_items``.
    """
    probe_qml = tmp_path / "gc_probe.qml"
    probe_qml.write_text("""
import QtQuick

Item {
    function touch() {
        const item = iface.findItemByObjectName("geometryHighlighter");
        item.duration = 4242;
    }
}
""")
    root = qfield_bot.load_qml(probe_qml)
    root.touch()

    assert QQmlEngine.objectOwnership(qfield_geometry_highlighter_stub) == (
        QQmlEngine.ObjectOwnership.CppOwnership
    )


@pytest.fixture
def feature_form_driver(
    qfield_bot: "QFieldBot",
    tmp_path: "Path",
    layer_points: "QgsVectorLayer",
    qgs_project_stub: "QgsProjectStub",
):
    """
    Drive ``featureForm`` through the canonical plugin pattern:
    grab via ``iface.findItemByObjectName('featureForm')``, navigate to a
    feature by attribute filter, focus the matched row, and switch state.
    """
    probe_qml = tmp_path / "feature_form_probe.qml"
    probe_qml.write_text("""
import QtQuick

Item {
    function open(filter, target_state) {
        const layer = qgisProject.mapLayersByName("points")[0];
        const form = iface.findItemByObjectName("featureForm");
        form.model.setFeatures(layer, filter);
        form.selection.focusedItem = 0;
        form.state = target_state;
    }
}
""")
    assert qgs_project_stub.qgis_project.addMapLayer(layer_points)
    root = qfield_bot.load_qml(probe_qml)
    return root, layer_points


def test_feature_list_form_records_canonical_plugin_pattern(
    feature_form_driver,
    qfield_feature_list_form_stub: QFieldFeatureListFormStub,
):
    root, _layer = feature_form_driver
    root.open("id = '42'", "FeatureFormEdit")

    calls = qfield_feature_list_form_stub.model.set_features_calls
    assert len(calls) == 1
    recorded_layer, recorded_filter = calls[0]
    # QML hands plugins the QgsVectorLayerStub, not the raw QgsVectorLayer;
    # verifying by name is enough to confirm the right layer made it through.
    assert recorded_layer.name == "points"
    assert recorded_filter == "id = '42'"
    assert qfield_feature_list_form_stub.selection.focusedItem == 0
    assert qfield_feature_list_form_stub.state == "FeatureFormEdit"


class _RecordingFeatureListFormStub(QFieldFeatureListFormStub):
    def __init__(self) -> None:
        super().__init__()
        self.state_history: list[str] = []
        self.stateChanged.connect(lambda: self.state_history.append(self.state))


def test_feature_list_form_can_be_overridden_via_fixture(
    qfield_bot: "QFieldBot",
    tmp_path: "Path",
    layer_points: "QgsVectorLayer",
    qgs_project_stub: "QgsProjectStub",
):
    custom = _RecordingFeatureListFormStub()
    # Same effect as redefining the fixture in conftest: swap the registered
    # named item before any QML loads. Tests in user repos override by
    # redefining ``qfield_feature_list_form_stub``; here we exercise the
    # register_named_item override path so the test stays self-contained.
    qfield_bot.iface.register_named_item("featureForm", custom)

    probe_qml = tmp_path / "feature_form_override.qml"
    probe_qml.write_text("""
import QtQuick

Item {
    function flip() {
        const form = iface.findItemByObjectName("featureForm");
        form.state = "FeatureForm";
        form.state = "FeatureFormEdit";
    }
}
""")
    assert qgs_project_stub.qgis_project.addMapLayer(layer_points)
    root = qfield_bot.load_qml(probe_qml)
    root.flip()

    assert custom.state_history == ["FeatureForm", "FeatureFormEdit"]
