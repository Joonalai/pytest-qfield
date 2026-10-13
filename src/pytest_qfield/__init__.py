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

try:
    from PyQt6 import QtQml, QtQuick  # noqa: F401
except ImportError as e:
    from PyQt6.QtCore import QT_VERSION_STR

    # The wheel must bundle the system Qt minor version, as QGIS uses its private API
    qt_minor = QT_VERSION_STR.rsplit(".", 1)[0]
    raise ImportError(
        f"{e.msg}. The PyQt6 of your QGIS installation lacks the QML bindings, "
        f"install them matching Qt {QT_VERSION_STR} with: "
        f'pip install "PyQt6=={qt_minor}.*"'
    ) from e
