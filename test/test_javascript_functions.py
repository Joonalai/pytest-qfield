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
from qgis.core import QgsVectorLayer

from pytest_qfield.stub_interface.qgis_stubs import QgsVectorLayerStub

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_subtests import SubTests

    from pytest_qfield.qfieldbot import QFieldBot
    from pytest_qfield.stub_interface.qgis_stubs import QgsProjectStub


@pytest.fixture
def js_directory(data_path: "Path") -> "Path":
    js_directory = data_path / "simple_plugin" / "js"
    assert js_directory.exists()
    return js_directory


def test_load_js_function(qfield_bot: "QFieldBot", js_directory: "Path"):
    js_object = qfield_bot.load_js_function(
        js_directory / "jslogic.js",
        "logHello",
        ["string"],
        extra_files=[js_directory / "another_file.js"],
    )
    assert js_object.call("return value") == "return value"
    assert qfield_bot.iface.logged_messages == [
        "Hello from JS!",
        "Log with another file",
    ]


def test_load_js_function_with_two_params(
    qfield_bot: "QFieldBot", js_directory: "Path"
):
    js_object = qfield_bot.load_js_function(
        js_directory / "jslogic.js",
        "sum",
        ["x", "y"],
        extra_files=[js_directory / "another_file.js"],
    )
    result = js_object.call(1, 2)
    assert qfield_bot.iface.logged_messages == ["Summing 1 and 2"]
    assert result == 3


@pytest.mark.usefixtures("qfield_new_project")
def test_qgis_project_map_layers_by_name(
    qfield_bot: "QFieldBot",
    qgs_project_stub: "QgsProjectStub",
    js_directory: "Path",
    subtests: "SubTests",
):
    js_object = qfield_bot.load_js_function(
        js_directory / "jslogic.js",
        "getLayer",
        ["string"],
        extra_files=[js_directory / "another_file.js"],
    )
    with subtests.test("non-existent layer should return None"):
        assert not js_object.call("nonexistent")

    with subtests.test("QObject layer can be used"):
        layer = QgsVectorLayer("Point", "foo", "memory")
        assert qgs_project_stub.qgis_project.addMapLayer(layer)
        returned_layer = js_object.call("foo")
        assert isinstance(returned_layer, QgsVectorLayerStub)
        assert returned_layer.name == "foo"
        assert qfield_bot.iface.logged_messages == ["Layer foo is valid!"]
