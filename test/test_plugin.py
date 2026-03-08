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
from unittest.mock import MagicMock

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_subtests import SubTests

    from pytest_qfield.qfieldbot import QFieldBot
    from pytest_qfield.stub_interface import QgsProjectStub


@pytest.fixture
def load_plugin(qfield_bot: "QFieldBot", data_path: "Path"):
    qfield_bot.load_plugin(
        data_path / "simple_plugin" / "main.qml", raise_if_warnings=True
    )
    qfield_bot.show_window()


@pytest.mark.usefixtures("load_plugin")
def test_qfield_bot_should_load_plugin(qfield_bot: "QFieldBot", subtests: "SubTests"):
    with subtests.test("button can be clicked"):
        button = qfield_bot.get_item("pluginButton")
        qfield_bot.click_item(button)
    with subtests.test("plugin log message is correct"):
        assert qfield_bot.iface.logged_messages == ["Plugin button clicked!"]
        assert qfield_bot.iface.toast_messages == ["Toast displayed!"]
    # Inspect visually that the button exists and the toast is visible
    # qfield_bot.qtbot.sleep(10000)


def test_load_js_function(qfield_bot: "QFieldBot", data_path: "Path"):
    js_object = qfield_bot.load_js_function(
        data_path / "simple_plugin" / "js" / "jslogic.js", "logHello", ["string"]
    )
    assert js_object.call("return value") == "return value"
    assert qfield_bot.iface.logged_messages == [
        "Hello from JS!",
    ]


def test_qgis_project_map_layers_by_name(
    qfield_bot: "QFieldBot",
    qgs_project_stub: "QgsProjectStub",
    data_path: "Path",
    subtests: "SubTests",
):
    js_object = qfield_bot.load_js_function(
        data_path / "simple_plugin" / "js" / "jslogic.js", "getLayer", ["string"]
    )
    with subtests.test("non-existent layer should return None"):
        assert not js_object.call("nonexistent")

    with subtests.test("MagickMock layer can be used"):
        layer = MagicMock()
        layer.name.return_value = "foo"

        qgs_project_stub.map_layers["foo"] = layer
        returned_layer = js_object.call("foo")
        assert returned_layer == layer
        assert returned_layer.name() == "foo"

    qgs_project_stub.map_layers.clear()
