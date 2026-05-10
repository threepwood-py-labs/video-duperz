from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType


def _load_package_release_module() -> ModuleType:
    """Load the standalone release packaging script as a Python module."""

    module_path = (
        Path(__file__).resolve().parents[2]
        / "scripts"
        / "windows"
        / "package_release.py"
    )
    spec = importlib.util.spec_from_file_location(
        "video_duperz_package_release",
        module_path,
    )
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_build_release_layout_falls_back_to_detected_dist_dir(tmp_path: Path) -> None:
    """Use the only discovered ``.dist`` folder when the name differs from output."""

    repo_root = tmp_path
    pyproject_path = repo_root / "pyproject.toml"
    pyproject_path.write_text(
        """
[project]
version = "0.1.1"

[tool.workspace.nuitka]
app_package = "video_duperz"
output_name = "video-duperz"
mode = "standalone"
windows_console_mode = "disable"
enable_plugins = ["pyside6"]
include_qt_plugins = ["platforms"]
include_data_files = []
""".strip(),
        encoding="utf-8",
    )
    dist_dir = repo_root / "build" / "nuitka" / "standalone" / "video_duperz.dist"
    dist_dir.mkdir(parents=True)

    package_release = _load_package_release_module()

    layout = package_release.build_release_layout(repo_root, "v0.1.1")

    assert layout.dist_dir == dist_dir
    assert layout.folder_name == "video-duperz-windows-x64-v0.1.1"
