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
from qgis.core import QgsPointXY, QgsRectangle

if TYPE_CHECKING:
    from pathlib import Path

    from qgis.core import QgsVectorLayer
    from qgis.gui import QgsMapCanvas

    from pytest_qfield.qfieldbot import QFieldBot
    from pytest_qfield.stub_interface.qgis_stubs import QgsProjectStub


@pytest.fixture
def load_stub_plugin_on_known_extent(
    qfield_bot: "QFieldBot",
    data_path: "Path",
    layer_points: "QgsVectorLayer",
    qgs_project_stub: "QgsProjectStub",
    qgis_canvas: "QgsMapCanvas",
):
    """Stub-tester plugin with the qgis_canvas pinned to a known extent so
    ``click_map_at`` produces predictable screen coords."""
    qgis_canvas.show()
    qgis_canvas.resize(200, 200)
    qgis_canvas.setExtent(QgsRectangle(0.0, 0.0, 200.0, 200.0))
    qgis_canvas.refresh()
    qfield_bot.show_window()
    qfield_bot.load_plugin(
        data_path / "stub_tester_plugin" / "main.qml",
        raise_if_warnings=True,
        emit_load_project_ended=False,
    )
    assert qgs_project_stub.qgis_project.addMapLayer(layer_points)
    qfield_bot.emit_load_project_ended()
    qfield_bot.iface.logged_messages.clear()


@pytest.mark.usefixtures("load_stub_plugin_on_known_extent")
def test_click_map_at_round_trips_through_screen_to_coordinate(
    qfield_bot: "QFieldBot",
):
    qfield_bot.click_map_at(QgsPointXY(120.0, 80.0))

    # The plugin handler calls screenToCoordinate on the emitted point and
    # logs the resulting CRS coord. The widget has small margins so the
    # round-trip can drift by a CRS unit or two.
    messages = qfield_bot.iface.logged_messages
    assert messages[2] == "clicked type: 0"
    assert float(messages[0].removeprefix("clicked x: ")) == pytest.approx(
        120.0, abs=2.0
    )
    assert float(messages[1].removeprefix("clicked y: ")) == pytest.approx(
        80.0, abs=2.0
    )


@pytest.mark.usefixtures("load_stub_plugin_on_known_extent")
def test_click_map_at_passes_click_type_through(qfield_bot: "QFieldBot"):
    qfield_bot.click_map_at(QgsPointXY(10.0, 10.0), click_type=1)
    assert qfield_bot.iface.logged_messages[2] == "clicked type: 1"


@pytest.mark.usefixtures("load_stub_plugin_on_known_extent")
def test_long_press_map_at_round_trips_through_screen_to_coordinate(
    qfield_bot: "QFieldBot",
):
    qfield_bot.long_press_map_at(QgsPointXY(50.0, 150.0))

    # stub_tester_plugin's confirmedClicked handler logs only x/y, not type.
    messages = qfield_bot.iface.logged_messages
    assert float(messages[0].removeprefix("confirmed x: ")) == pytest.approx(
        50.0, abs=2.0
    )
    assert float(messages[1].removeprefix("confirmed y: ")) == pytest.approx(
        150.0, abs=2.0
    )


@pytest.mark.parametrize(
    "blocker_parent",
    ["plugin", "iface.mainWindow().contentItem"],
    ids=["plugin", "content"],
)
def test_click_item_taps_full_map_overlay_at_canvas_coordinate(
    qfield_bot: "QFieldBot",
    qgis_canvas: "QgsMapCanvas",
    tmp_path: "Path",
    blocker_parent: str,
):
    plugin_qml = tmp_path / "overlay_plugin.qml"
    plugin_qml.write_text(f"""
import QtQuick

Item {{
    id: plugin

    Item {{
        objectName: "mapClickBlocker"
        parent: {blocker_parent}
        anchors.fill: parent

        TapHandler {{
            onTapped: (eventPoint) => {{
                const point = iface.mapCanvas().mapSettings.screenToCoordinate(
                    eventPoint.position
                );
                iface.logMessage(point.x + "," + point.y);
            }}
        }}
    }}
}}
""")
    qfield_bot.show_window()
    qgis_canvas.setExtent(QgsRectangle(0.0, 0.0, 200.0, 200.0))
    qfield_bot.load_plugin(plugin_qml, emit_load_project_ended=False)
    blocker = qfield_bot.get_item("mapClickBlocker")

    qfield_bot.click_item(blocker)

    window = blocker.window()
    assert (window.width(), window.height()) == (
        qgis_canvas.width(),
        qgis_canvas.height(),
    )
    expected = qgis_canvas.getCoordinateTransform().toMapCoordinates(
        window.width() // 2, window.height() // 2
    )
    [message] = qfield_bot.iface.logged_messages
    x, y = (float(value) for value in message.split(","))
    assert x == pytest.approx(expected.x(), abs=1.0)
    assert y == pytest.approx(expected.y(), abs=1.0)


def test_click_item_raises_when_item_is_outside_window(
    qfield_bot: "QFieldBot",
    tmp_path: "Path",
):
    plugin_qml = tmp_path / "offscreen_plugin.qml"
    plugin_qml.write_text("""
import QtQuick

Item {
    Item {
        objectName: "farAway"
        x: 100000
        y: 100000
        width: 10
        height: 10
    }
}
""")
    qfield_bot.load_plugin(plugin_qml, emit_load_project_ended=False)

    with pytest.raises(RuntimeError, match="outside"):
        qfield_bot.click_item(qfield_bot.get_item("farAway"))
