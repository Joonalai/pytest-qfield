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


import shutil
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from qgis.core import QgsRasterLayer, QgsVectorLayer

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

    from pytest_qfield.qfieldbot import QFieldBot


@pytest.fixture(autouse=True)
def setup(qfield_new_project):
    pass


@pytest.fixture(scope="session")
def data_path() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture
def mock_uuid_value(mocker: "MockerFixture") -> str:
    return mocker.patch("uuid.uuid4", return_value="random-uuid-value")


@pytest.fixture
def load_simple_plugin(qfield_bot: "QFieldBot", data_path: "Path"):
    qfield_bot.load_plugin(
        data_path / "simple_plugin" / "main.qml", raise_if_warnings=True
    )
    qfield_bot.show_window()


@pytest.fixture
def load_simple_plugin_without_project_loaded_signal(
    qfield_bot: "QFieldBot", data_path: "Path"
):
    qfield_bot.load_plugin(
        data_path / "simple_plugin" / "main.qml", emit_load_project_ended=False
    )
    qfield_bot.show_window()
    assert qfield_bot.iface.logged_messages == []


@pytest.fixture
def project_loaded(qfield_bot: "QFieldBot", qfield_project_file: "Path"):
    qfield_bot.open_project(qfield_project_file)


@pytest.fixture
def qfield_project_file(tmp_path: Path, data_path: Path) -> Path:
    copied_project = get_copied_path(tmp_path, data_path / "qfield_project")
    project_file = copied_project / "pytest-qfield-project_qfield.qgs"
    assert project_file.exists()
    return project_file


@pytest.fixture
def gpkg(tmp_path: Path, data_path: Path) -> Path:
    return get_copied_gpkg(tmp_path, data_path)


@pytest.fixture(scope="module")
def gpkg_module(tmpdir_factory, data_path: Path) -> Path:
    tmp_path = Path(tmpdir_factory.mktemp("pytest_qgis_data"))
    return get_copied_gpkg(tmp_path, data_path)


@pytest.fixture(scope="session")
def gpkg_session(tmpdir_factory, data_path: Path) -> Path:
    tmp_path = Path(tmpdir_factory.mktemp("pytest_qgis_data"))
    return get_copied_gpkg(tmp_path, data_path)


@pytest.fixture
def layer_polygon(gpkg: Path):
    return get_gpkg_layer("polygon", gpkg)


@pytest.fixture
def layer_polygon_3067(gpkg: Path):
    return get_gpkg_layer("polygon_3067", gpkg)


@pytest.fixture
def layer_points(gpkg: Path):
    return get_gpkg_layer("points", gpkg)


def get_copied_gpkg(tmp_path: Path, data_path: Path) -> Path:
    return get_copied_path(tmp_path, data_path / "qgis_project" / "db.gpkg")


def get_copied_path(tmp_path: Path, path: Path) -> Path:
    new_path = tmp_path / path.name
    if path.is_dir():
        shutil.copytree(path, new_path)
    else:
        shutil.copy(path, new_path)
    return new_path


def get_gpkg_layer(name: str, gpkg: Path) -> QgsVectorLayer:
    layer = QgsVectorLayer(f"{gpkg!s}|layername={name}", name, "ogr")
    layer.setProviderEncoding("utf-8")
    assert layer.isValid()
    assert layer.crs().isValid()
    return layer


def get_raster_layer(name: str, path: Path) -> QgsRasterLayer:
    layer = QgsRasterLayer(str(path), name)
    assert layer.isValid()
    return layer
