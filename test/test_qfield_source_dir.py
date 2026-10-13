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
from pathlib import Path

import pytest

from pytest_qfield.plugin import _get_qfield_source_path


class _ConfigStub:
    def __init__(self, ini_values: dict[str, str]) -> None:
        self._ini_values = ini_values

    def getini(self, name: str) -> str:
        return self._ini_values.get(name, "")


@pytest.fixture
def qfield_checkout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    for env_var in ("QFIELD_SOURCE_DIR", "QFIELD_IMPORTS_DIR"):
        monkeypatch.delenv(env_var, raising=False)
    # Resolved because the plugin resolves, and tmp dirs can be symlinks (macOS)
    qfield_checkout = tmp_path.resolve()
    (qfield_checkout / "src" / "gui" / "qml").mkdir(parents=True)
    return qfield_checkout


def test_source_dir_is_read_from_env(
    qfield_checkout: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("QFIELD_SOURCE_DIR", str(qfield_checkout))

    assert _get_qfield_source_path(_ConfigStub({})) == qfield_checkout


def test_source_dir_ini_value_takes_precedence_over_env(
    qfield_checkout: Path,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path_factory: pytest.TempPathFactory,
):
    monkeypatch.setenv("QFIELD_SOURCE_DIR", str(tmp_path_factory.mktemp("other")))
    config = _ConfigStub({"qfield_source_dir": str(qfield_checkout)})

    assert _get_qfield_source_path(config) == qfield_checkout


@pytest.mark.parametrize("qml_dir", ["src/gui/qml", "src/qml/imports"])
def test_qml_dir_suffix_is_stripped(
    qfield_checkout: Path, monkeypatch: pytest.MonkeyPatch, qml_dir: str
):
    monkeypatch.setenv("QFIELD_SOURCE_DIR", str(qfield_checkout / qml_dir))

    assert _get_qfield_source_path(_ConfigStub({})) == qfield_checkout


def test_relative_source_dir_is_resolved(
    qfield_checkout: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.chdir(qfield_checkout.parent)
    monkeypatch.setenv("QFIELD_SOURCE_DIR", qfield_checkout.name)

    assert _get_qfield_source_path(_ConfigStub({})) == qfield_checkout


def test_deprecated_env_var_is_supported_with_warning(
    qfield_checkout: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("QFIELD_IMPORTS_DIR", str(qfield_checkout / "src/gui/qml"))

    with pytest.warns(DeprecationWarning, match="QFIELD_IMPORTS_DIR"):
        assert _get_qfield_source_path(_ConfigStub({})) == qfield_checkout


def test_deprecated_ini_value_is_supported_with_warning(qfield_checkout: Path):
    config = _ConfigStub({"qfield_imports_dir": str(qfield_checkout)})

    with pytest.warns(DeprecationWarning, match="qfield_imports_dir"):
        assert _get_qfield_source_path(config) == qfield_checkout


def test_missing_source_dir_raises(qfield_checkout: Path):  # noqa: ARG001
    with pytest.raises(ValueError, match="QFIELD_SOURCE_DIR"):
        _get_qfield_source_path(_ConfigStub({}))


def test_non_qfield_dir_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("QFIELD_SOURCE_DIR", str(tmp_path))

    with pytest.raises(ValueError, match="not a QField source checkout"):
        _get_qfield_source_path(_ConfigStub({}))
