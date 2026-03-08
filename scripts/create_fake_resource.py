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

import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

QML_CONTENT = """
import QtQuick
import QtQuick.Controls

Button {
}

"""

QRC_CONTENT = """
<RCC>
    <qresource prefix="/qml">
        <file>test.qml</file>
    </qresource>
</RCC>
"""


def main() -> None:
    output_path = Path(__file__).parent.parent.joinpath(
        "src", "pytest_qfield", "qfield_resources.py"
    )

    with TemporaryDirectory() as temp_dir:
        qml_file = Path(temp_dir) / "test.qml"
        qml_file.touch()
        qml_file.write_text(QML_CONTENT)

        qrc_file = Path(temp_dir) / "resources.qrc"
        qrc_file.touch()
        qrc_file.write_text(QRC_CONTENT)

        temp_output = Path(temp_dir) / "resources.py"

        subprocess.run(
            ["rcc", "-g", "python", str(qrc_file), "-o", str(temp_output)], check=True
        )

        if not temp_output.exists():
            raise ValueError(f"Output path {temp_output} was not created!")

        resources_content = temp_output.read_text()

        if not output_path.exists():
            output_path.touch()

        output_path.write_text(resources_content.replace("PySide2", "PyQt6"))


if __name__ == "__main__":
    main()
