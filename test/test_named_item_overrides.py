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

from pytest_qfield.stub_interface.qfield_stubs import QFieldPositioningStub

if TYPE_CHECKING:
    from pathlib import Path

    from qgis.core import QgsVectorLayer

    from pytest_qfield.qfieldbot import QFieldBot
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
