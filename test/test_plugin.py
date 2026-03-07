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

    from pytest_subtests import SubTests

    from pytest_qfield.qfieldbot import QFieldBot


@pytest.fixture
def load_plugin(qfield_bot: "QFieldBot", data_path: "Path"):
    qfield_bot.load_plugin(data_path / "simple_plugin" / "main.qml")


@pytest.mark.usefixtures("load_plugin")
def test_qfield_bot_should_load_plugin(qfield_bot: "QFieldBot", subtests: "SubTests"):
    with subtests.test("button can be clicked"):
        button = qfield_bot.get_item("pluginButton")
        qfield_bot.click_item(button)
    with subtests.test("plugin log message is correct"):
        assert qfield_bot.iface.logged_messages == ["Plugin button clicked!"]


def test_load_js_function(qfield_bot: "QFieldBot", data_path: "Path"):
    js_object = qfield_bot.load_js_function(
        data_path / "simple_plugin" / "js" / "jslogic.js", "logHello", ["string"]
    )
    assert js_object.call("return value") == "return value"
    assert qfield_bot.iface.logged_messages == [
        "Hello from JS!",
    ]
