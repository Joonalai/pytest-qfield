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
Covers the stub surface that lets a project form button trigger a plugin action
through the shared ``settings`` global (the only channel that reaches a cloud
"project plugin"): the button writes a token, the plugin polls and consumes it,
then reads the focused occurrence from ``featureForm.selection``.
"""

from typing import TYPE_CHECKING

import pytest
from PyQt6.QtCore import QSettings

from pytest_qfield.stub_interface.qgis_stubs import QSettingsStub

if TYPE_CHECKING:
    from pathlib import Path

    from qgis.core import QgsVectorLayer

    from pytest_qfield.qfieldbot import QFieldBot
    from pytest_qfield.stub_interface.qgis_stubs import QgsProjectStub


@pytest.fixture
def qfield_settings_stub(tmp_path: "Path") -> QSettingsStub:
    """Isolate settings per test in a temp ini file instead of the shared store."""
    return QSettingsStub(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)


def test_settings_set_value_and_remove_round_trip_from_qml(
    qfield_bot: "QFieldBot",
    tmp_path: "Path",
):
    probe_qml = tmp_path / "settings_probe.qml"
    probe_qml.write_text("""
import QtQuick

Item {
    function run() {
        settings.setValue("myplugin/action", "redrawSamplePlots");
        iface.logMessage("after set: " + settings.value("myplugin/action", ""));
        settings.remove("myplugin/action");
        iface.logMessage("after remove: " + settings.value("myplugin/action", ""));
    }
}
""")
    root = qfield_bot.load_qml(probe_qml)
    root.run()

    assert qfield_bot.iface.logged_messages == [
        "after set: redrawSamplePlots",
        "after remove: ",
    ]


def test_focused_feature_and_layer_resolve_from_setfeatures(
    qfield_bot: "QFieldBot",
    layer_points: "QgsVectorLayer",
    qgs_project_stub: "QgsProjectStub",
):
    assert qgs_project_stub.qgis_project.addMapLayer(layer_points)
    [layer_stub] = qgs_project_stub.mapLayersByName("points")
    selection = qfield_bot.iface.findItemByObjectName("featureForm").selection

    # Nothing focused yet.
    assert selection.focusedFeature is None
    assert selection.focusedLayer is None

    # The flow a plugin uses to open a form.
    qfield_bot.iface.findItemByObjectName("featureForm").model.setFeatures(
        layer_stub, "fid = 1"
    )
    selection.focusedItem = 0

    assert selection.focusedLayer.name == "points"  # type: ignore[attr-defined]
    feature = selection.focusedFeature
    assert feature is not None
    assert feature.id == 1
    assert feature.attribute("text_field") == "test"


def test_settings_poll_consumes_token_and_reads_focused_occurrence(
    qfield_bot: "QFieldBot",
    tmp_path: "Path",
    layer_points: "QgsVectorLayer",
    qgs_project_stub: "QgsProjectStub",
    qfield_settings_stub: QSettingsStub,
):
    """
    Exercises the whole channel end to end: a Timer-driven poll (as the plugin
    runs) reads the token a form button wrote, consumes it, and resolves the
    focused feature — the path that is otherwise only verified manually.
    """
    assert qgs_project_stub.qgis_project.addMapLayer(layer_points)
    [layer_stub] = qgs_project_stub.mapLayersByName("points")

    probe_qml = tmp_path / "poll_probe.qml"
    probe_qml.write_text("""
import QtQuick

Item {
    property string lastAction: ""
    property int focusedId: -1

    Timer {
        interval: 50
        running: true
        repeat: true
        onTriggered: {
            const action = settings.value("myplugin/action", "");
            if (action !== "") {
                settings.remove("myplugin/action");
                const form = iface.findItemByObjectName("featureForm");
                lastAction = action;
                focusedId = form.selection.focusedFeature.id;
            }
        }
    }
}
""")
    root = qfield_bot.load_qml(probe_qml)

    # Focus the occurrence, then write the action token as the form button does.
    form = qfield_bot.iface.findItemByObjectName("featureForm")
    form.model.setFeatures(layer_stub, "fid = 1")
    form.selection.focusedItem = 0
    qfield_settings_stub.setValue("myplugin/action", "redrawSamplePlots")  # noqa: QGS202

    qfield_bot.qtbot.wait(60)

    assert root.property("lastAction") == "redrawSamplePlots"
    assert root.property("focusedId") == 1
    assert qfield_settings_stub.value("myplugin/action", "") == ""
