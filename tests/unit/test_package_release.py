from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType


def _load_windows_script(module_name: str, script_name: str) -> ModuleType:
    """Load one standalone Windows helper script as a Python module."""

    scripts_dir = Path(__file__).resolve().parents[2] / "scripts" / "windows"
    module_path = scripts_dir / script_name
    spec = importlib.util.spec_from_file_location(
        module_name,
        module_path,
    )
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(scripts_dir))
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(scripts_dir))
    return module


def _load_package_release_module() -> ModuleType:
    """Load the standalone release packaging script as a Python module."""

    return _load_windows_script("video_duperz_package_release", "package_release.py")


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
    assert layout.target_arch == "windows-x64"
    assert layout.folder_name == "video-duperz-windows-x64-v0.1.1"

    arm64_layout = package_release.build_release_layout(
        repo_root,
        "v0.1.1",
        "windows-arm64",
    )
    assert arm64_layout.target_arch == "windows-arm64"
    assert arm64_layout.folder_name == "video-duperz-windows-arm64-v0.1.1"


def test_build_onefile_config_forces_onefile_mode(tmp_path: Path) -> None:
    """Onefile builds override the shared Nuitka mode without editing config."""

    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(
        """
[tool.workspace.nuitka]
app_package = "video_duperz"
output_name = "video-duperz"
mode = "standalone"
windows_console_mode = "disable"
enable_plugins = ["pyside6"]
include_qt_plugins = []
include_data_files = []
""".strip(),
        encoding="utf-8",
    )
    build_onefile = _load_windows_script(
        "video_duperz_build_onefile",
        "build_onefile.py",
    )

    config = build_onefile.load_onefile_nuitka_config(tmp_path)

    assert config.mode == "onefile"
    assert config.output_name == "video-duperz"


def test_build_onefile_layout_uses_public_exe_name(tmp_path: Path) -> None:
    """Stage the onefile executable with the public release asset name."""

    pyproject_path = tmp_path / "pyproject.toml"
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
include_qt_plugins = []
include_data_files = []
""".strip(),
        encoding="utf-8",
    )
    source_exe = tmp_path / "build" / "nuitka" / "onefile" / "video-duperz.exe"
    source_exe.parent.mkdir(parents=True)
    source_exe.write_bytes(b"fake exe")
    package_onefile = _load_windows_script(
        "video_duperz_package_onefile",
        "package_onefile.py",
    )

    layout = package_onefile.build_onefile_layout(tmp_path, "v0.1.1")
    package_onefile.stage_onefile(layout)

    expected_exe = (
        tmp_path / "build" / "release" / "video-duperz-v0.1.1-windows-x64.exe"
    )
    assert layout.source_exe == source_exe
    assert layout.target_arch == "windows-x64"
    assert layout.release_exe == expected_exe
    assert expected_exe.read_bytes() == b"fake exe"

    arm64_layout = package_onefile.build_onefile_layout(
        tmp_path,
        "v0.1.1",
        "windows-arm64",
    )
    assert arm64_layout.target_arch == "windows-arm64"
    assert (
        arm64_layout.release_exe
        == tmp_path / "build" / "release" / "video-duperz-v0.1.1-windows-arm64.exe"
    )


def test_write_release_checksums_includes_exe_and_zip(tmp_path: Path) -> None:
    """Generate checksums for public executable and zip release assets."""

    release_dir = tmp_path / "build" / "release"
    release_dir.mkdir(parents=True)
    exe_path = release_dir / "video-duperz-v0.1.1-windows-x64.exe"
    zip_path = release_dir / "video-duperz-windows-x64-v0.1.1.zip"
    exe_path.write_bytes(b"fake exe")
    zip_path.write_bytes(b"fake zip")
    checksums = _load_windows_script(
        "video_duperz_write_release_checksums",
        "write_release_checksums.py",
    )

    checksum_path = checksums.write_checksums(release_dir)

    checksum_text = checksum_path.read_text(encoding="utf-8")
    assert "video-duperz-v0.1.1-windows-x64.exe" in checksum_text
    assert "video-duperz-windows-x64-v0.1.1.zip" in checksum_text


def test_verify_release_assets_accepts_complete_multi_arch_set(tmp_path: Path) -> None:
    """Verify every public asset has a matching checksum entry."""

    release_dir = tmp_path / "build" / "release"
    release_dir.mkdir(parents=True)
    asset_names = [
        "video-duperz-v0.1.1-windows-x64.exe",
        "video-duperz-v0.1.1-windows-arm64.exe",
        "video-duperz-windows-x64-v0.1.1.zip",
        "video-duperz-windows-arm64-v0.1.1.zip",
    ]
    for asset_name in asset_names:
        (release_dir / asset_name).write_bytes(asset_name.encode("utf-8"))
    checksums = _load_windows_script(
        "video_duperz_write_release_checksums_verify",
        "write_release_checksums.py",
    )
    checksums.write_checksums(release_dir)
    verifier = _load_windows_script(
        "video_duperz_verify_release_assets",
        "verify_release_assets.py",
    )

    verifier.verify_release_assets(release_dir, "v0.1.1")


def test_verify_release_assets_rejects_missing_checksum(tmp_path: Path) -> None:
    """Fail release verification when an asset lacks a checksum."""

    release_dir = tmp_path / "build" / "release"
    release_dir.mkdir(parents=True)
    for asset_name in [
        "video-duperz-v0.1.1-windows-x64.exe",
        "video-duperz-v0.1.1-windows-arm64.exe",
        "video-duperz-windows-x64-v0.1.1.zip",
        "video-duperz-windows-arm64-v0.1.1.zip",
    ]:
        (release_dir / asset_name).write_bytes(b"asset")
    (release_dir / "SHA256SUMS.txt").write_text(
        "0" * 64 + "  video-duperz-v0.1.1-windows-x64.exe\n",
        encoding="utf-8",
    )
    verifier = _load_windows_script(
        "video_duperz_verify_release_assets_missing_checksum",
        "verify_release_assets.py",
    )

    with pytest.raises(ValueError, match="Missing checksums"):
        verifier.verify_release_assets(release_dir, "v0.1.1")
