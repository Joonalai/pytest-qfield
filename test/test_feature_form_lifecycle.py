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

if TYPE_CHECKING:
    from pathlib import Path

    from qgis.core import QgsVectorLayer

    from pytest_qfield.qfieldbot import QFieldBot
    from pytest_qfield.stub_interface.qfield_stubs import (
        QFieldFeatureListFormStub,
        QFieldOverlayFeatureFormDrawerStub,
    )
    from pytest_qfield.stub_interface.qgis_stubs import QgsProjectStub


def test_open_feature_form_view_makes_form_visible_and_sets_state(
    qfield_bot: "QFieldBot",
    layer_points: "QgsVectorLayer",
    qfield_feature_list_form_stub: "QFieldFeatureListFormStub",
):
    qfield_bot.open_feature_form(layer_points, 42, mode="view")

    assert qfield_feature_list_form_stub.visible is True
    assert qfield_feature_list_form_stub.state == "FeatureForm"
    assert qfield_feature_list_form_stub.selection.focusedItem == 0
    calls = qfield_feature_list_form_stub.model.set_features_calls
    assert len(calls) == 1
    recorded_layer, recorded_filter = calls[0]
    assert recorded_layer.name == "points"
    assert recorded_filter == "$id = 42"


def test_open_feature_form_edit_sets_edit_state(
    qfield_bot: "QFieldBot",
    layer_points: "QgsVectorLayer",
    qfield_feature_list_form_stub: "QFieldFeatureListFormStub",
):
    qfield_bot.open_feature_form(layer_points, 1, mode="edit")

    assert qfield_feature_list_form_stub.visible is True
    assert qfield_feature_list_form_stub.state == "FeatureFormEdit"


def test_open_feature_form_rejects_unknown_mode(
    qfield_bot: "QFieldBot",
    layer_points: "QgsVectorLayer",
):
    with pytest.raises(ValueError, match="Unknown feature form mode 'bogus'"):
        qfield_bot.open_feature_form(layer_points, 1, mode="bogus")


def test_close_forms_hides_feature_form(
    qfield_bot: "QFieldBot",
    layer_points: "QgsVectorLayer",
    qfield_feature_list_form_stub: "QFieldFeatureListFormStub",
):
    qfield_bot.open_feature_form(layer_points, 1, mode="view")
    qfield_bot.close_forms()

    assert qfield_feature_list_form_stub.visible is False
    assert qfield_feature_list_form_stub.state == "Hidden"


def test_open_overlay_form_sets_opened_and_records_feature(
    qfield_bot: "QFieldBot",
    layer_points: "QgsVectorLayer",
    qfield_overlay_feature_form_drawer_stub: "QFieldOverlayFeatureFormDrawerStub",
):
    qfield_bot.open_overlay_form(layer_points, 7)

    assert qfield_overlay_feature_form_drawer_stub.opened is True
    shown = qfield_overlay_feature_form_drawer_stub.shown_features
    assert len(shown) == 1
    recorded_layer, recorded_feature_id = shown[0]
    assert recorded_layer.name == "points"
    assert recorded_feature_id == 7

    qfield_bot.close_forms()
    assert qfield_overlay_feature_form_drawer_stub.opened is False


def test_form_lifecycle_drives_qml_binding(
    qfield_bot: "QFieldBot",
    tmp_path: "Path",
    layer_points: "QgsVectorLayer",
    qgs_project_stub: "QgsProjectStub",
):
    """
    A plugin binding `aFormIsOpen` to the two stubs (as the myplugin plugin does)
    must flip as the bot opens and closes forms. This is the surface that lets
    the read-only `"FeatureForm"` view case be tested at all.
    """
    probe_qml = tmp_path / "a_form_is_open_probe.qml"
    probe_qml.write_text("""
import QtQuick

Item {
    property var featureForm: iface.findItemByObjectName("featureForm")
    property var overlayFeatureFormDrawer: iface.findItemByObjectName("overlayFeatureFormDrawer")
    readonly property bool aFormIsOpen: (!!featureForm && featureForm.visible === true)
        || (!!overlayFeatureFormDrawer && overlayFeatureFormDrawer.opened === true)
}
""")
    assert qgs_project_stub.qgis_project.addMapLayer(layer_points)
    root = qfield_bot.load_qml(probe_qml)
    assert root.property("aFormIsOpen") is False

    qfield_bot.open_feature_form(layer_points, 1, mode="view")
    assert root.property("aFormIsOpen") is True

    qfield_bot.close_forms()
    assert root.property("aFormIsOpen") is False

    qfield_bot.open_overlay_form(layer_points, 1)
    assert root.property("aFormIsOpen") is True

    qfield_bot.close_forms()
    assert root.property("aFormIsOpen") is False
