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

from pytest_field_test_utils.env import IN_CI

if TYPE_CHECKING:
    from qgis.core import QgsVectorLayer

    from pytest_qfield.qfieldbot import QFieldBot
    from pytest_qfield.stub_interface.qgis_stubs import QgsProjectStub

DEFAULT_TIMEOUT = 0.01 if IN_CI else 1


@pytest.mark.qgis_show_map(DEFAULT_TIMEOUT)
@pytest.mark.usefixtures("load_simple_plugin")
def test_qfield_bot_should_load_plugin(qfield_bot: "QFieldBot"):
    # Inspect visually that the button exists and the toast is visible
    qfield_bot.click_item(qfield_bot.get_item("pluginButton"))


@pytest.mark.qgis_show_map(DEFAULT_TIMEOUT)
@pytest.mark.usefixtures("load_simple_plugin")
def test_vector_layer_should_be_visible_in_app(
    qfield_bot: "QFieldBot",
    layer_points: "QgsVectorLayer",
    qgs_project_stub: "QgsProjectStub",
):
    assert qgs_project_stub.qgis_project.addMapLayer(layer_points)
    qfield_bot.iface.qgis_map_canvas.setExtent(layer_points.extent())


@pytest.mark.qgis_show_map(DEFAULT_TIMEOUT)
@pytest.mark.usefixtures("load_simple_plugin")
def test_vector_layer_with_non_default_crs_should_be_visible_in_app(
    qfield_bot: "QFieldBot",
    layer_polygon_3067: "QgsVectorLayer",
    qgs_project_stub: "QgsProjectStub",
):
    assert qgs_project_stub.qgis_project.addMapLayer(layer_polygon_3067)
    qfield_bot.set_map_crs_based_on_layers()
    qfield_bot.iface.qgis_map_canvas.setExtent(layer_polygon_3067.extent())


@pytest.mark.usefixtures(
    "load_simple_plugin_without_project_loaded_signal", "project_loaded"
)
def test_qfield_bot_should_open_project_file_and_layers_should_be_visible(
    qfield_bot: "QFieldBot",
):
    # TODO: cannot use qgis_show_map since it tries to reproject the web map
    qfield_bot.qtbot.wait(DEFAULT_TIMEOUT * 1000)
