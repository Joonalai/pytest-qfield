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

from pytest_qfield.stub_interface.qfield_stubs import (
    QFieldGeometryHighlighterStub,
    QFieldPositioningStub,
)

if TYPE_CHECKING:
    from pathlib import Path

    from qgis.core import QgsVectorLayer

    from pytest_qfield.qfieldbot import QFieldBot
    from pytest_qfield.stub_interface.qgis_stubs import QgsProjectStub


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
    assert qfield_bot.iface.logged_messages == ["Setup complete"]
    qfield_bot.iface.logged_messages.clear()


@pytest.mark.usefixtures("load_stub_plugin")
def test_feature_can_be_created_with_stub_interface(
    qfield_bot: "QFieldBot", layer_points: "QgsVectorLayer"
):
    initial_feature_ids = set(layer_points.allFeatureIds())
    qfield_bot.click_item(qfield_bot.get_item("test_creating_feature"))
    assert qfield_bot.iface.logged_messages == [
        "Geometry: Point (2 2)",
        "Feature created",
        "Editing started: true",
        "Feature added: -2",
        "Feature added: true",
        "Feature added: 11",
        "Committed changes: true",
    ]
    new_feature_ids = set(layer_points.allFeatureIds())
    assert len(new_feature_ids) == len(initial_feature_ids) + 1
    new_feature_id = new_feature_ids.difference(initial_feature_ids).pop()
    feature = layer_points.getFeature(new_feature_id)
    assert feature.isValid()
    assert feature.geometry().asWkt(1) == "Point (1.5 2.4)"
    assert feature["text_field"] == "new_value"


@pytest.mark.usefixtures("load_stub_plugin")
def test_features_can_be_iterated_with_stub_interface(qfield_bot: "QFieldBot"):
    button = qfield_bot.get_item("test_feature_iterator")
    qfield_bot.click_item(button)
    assert qfield_bot.iface.logged_messages == [
        "Feature found: 1",
        "Geometry: Point (24 67)",
    ]


@pytest.mark.usefixtures("load_stub_plugin")
def test_position_source_is_auto_registered_with_default_values(
    qfield_bot: "QFieldBot",
):
    qfield_bot.click_item(qfield_bot.get_item("test_position_source"))
    assert qfield_bot.iface.logged_messages == [
        "positionSource active: true",
        "positionSource x: 0",
        "positionSource y: 0",
    ]


@pytest.mark.usefixtures("load_stub_plugin")
def test_geometry_highlighter_is_auto_registered_and_mutable_from_qml(
    qfield_bot: "QFieldBot",
):
    qfield_bot.click_item(qfield_bot.get_item("test_geometry_highlighter"))
    assert qfield_bot.iface.logged_messages == [
        "highlighter visible: true",
        "highlighter duration: 1500",
        "highlighter geometry: Point (1 2)",
        "highlighter geometry after clear: undefined",
    ]


@pytest.mark.usefixtures("load_stub_plugin")
def test_unknown_object_name_resolves_to_null(qfield_bot: "QFieldBot"):
    qfield_bot.click_item(qfield_bot.get_item("test_unknown_named_item"))
    assert qfield_bot.iface.logged_messages == ["unknown is null: true"]


def test_positioning_stub_exposes_constructor_arguments() -> None:
    stub = QFieldPositioningStub(x=10.5, y=-20.25, active=False)
    assert stub.active is False
    assert stub.projectedPosition.x == 10.5
    assert stub.projectedPosition.y == -20.25


def test_geometry_highlighter_stub_clear_resets_wrapper_fields() -> None:
    stub = QFieldGeometryHighlighterStub()
    stub.geometryWrapper.crs = "EPSG:3067"
    stub.geometryWrapper.qgsGeometry = "POINT(1 1)"
    stub.geometryWrapper.clear()
    assert stub.geometryWrapper.crs is None
    assert stub.geometryWrapper.qgsGeometry is None
