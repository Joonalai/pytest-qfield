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
"""
Example: overriding stub fixtures to customize QML behavior.

All stub fixtures provided by pytest-qfield can be overridden in your
conftest.py.  This file demonstrates the pattern by subclassing
QFieldStringUtilsStub so that ``StringUtils.createUuid()`` returns a
deterministic value instead of a random UUID.
"""

from typing import TYPE_CHECKING

import pytest
from PyQt6.QtCore import pyqtSlot

from pytest_qfield.stub_interface.qfield_stubs import QFieldStringUtilsStub

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_qfield.qfieldbot import QFieldBot


# ---------------------------------------------------------------------------
# 1. Subclass the stub you want to change
# ---------------------------------------------------------------------------
class DeterministicStringUtils(QFieldStringUtilsStub):
    """StringUtils stub that always returns the same UUID."""

    @pyqtSlot(result=str)
    def createUuid(self) -> str:
        return "{00000000-0000-0000-0000-000000000000}"


# ---------------------------------------------------------------------------
# 2. Override the fixture (in your conftest.py or test module)
# ---------------------------------------------------------------------------
@pytest.fixture
def qfield_string_utils_stub() -> QFieldStringUtilsStub:
    return DeterministicStringUtils()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
@pytest.fixture
def load_simple_plugin(qfield_bot: "QFieldBot", data_path: "Path"):
    qfield_bot.load_plugin(
        data_path / "simple_plugin" / "main.qml", raise_if_warnings=True
    )
    qfield_bot.show_window()


# ---------------------------------------------------------------------------
# 3. Test that the overridden stub is used by QML
# ---------------------------------------------------------------------------
@pytest.mark.usefixtures("load_simple_plugin")
def test_overridden_string_utils_is_used_by_qml(qfield_bot: "QFieldBot"):
    """The simple_plugin calls StringUtils.createUuid() on button click."""
    button = qfield_bot.get_item("pluginButton")
    qfield_bot.click_item(button)

    # The plugin logs the UUID value returned by StringUtils.createUuid().
    # Because we overrode the fixture, it should be our deterministic value.
    assert qfield_bot.iface.logged_messages == [
        "Project load ended",
        "Plugin button clicked!",
        "UUID value:",
        "{00000000-0000-0000-0000-000000000000}",
    ]
