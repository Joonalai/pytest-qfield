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
    from unittest.mock import MagicMock

    from pytest_subtests import SubTests

    from pytest_qfield.qfieldbot import QFieldBot
    from pytest_qfield.stub_interface.qgis_stubs import QgsProjectStub


@pytest.mark.usefixtures("load_simple_plugin")
def test_qfield_bot_should_load_plugin(
    qfield_bot: "QFieldBot", subtests: "SubTests", mock_uuid_value: "MagicMock"
):
    with subtests.test("button can be clicked"):
        button = qfield_bot.get_item("pluginButton")
        qfield_bot.click_item(button)
    with subtests.test("plugin log message is correct"):
        mock_uuid_value.assert_called_once()
        assert qfield_bot.iface.logged_messages == [
            "Project load ended",
            "Plugin button clicked!",
            "UUID value:",
            "{random-uuid-value}",
        ]
        assert qfield_bot.iface.toast_messages == ["Toast displayed!"]


@pytest.mark.usefixtures(
    "load_simple_plugin_without_project_loaded_signal", "project_loaded"
)
def test_qfield_bot_should_open_project_file(
    qfield_bot: "QFieldBot", qgs_project_stub: "QgsProjectStub"
):
    assert qfield_bot.iface.logged_messages == ["Project load ended"]
    assert len(qgs_project_stub.mapLayersByName("points")) == 1
    osm_layers = qgs_project_stub.mapLayersByName("OpenStreetMap")
    assert osm_layers, "Expected 'OpenStreetMap' layer in project"
    osm_layer = osm_layers[0]
    assert osm_layer.isValid, "OpenStreetMap layer is invalid"
