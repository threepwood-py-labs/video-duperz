"""Assemble the public portable release zip from the Nuitka standalone output."""

from __future__ import annotations

import argparse
import shutil
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

OFFLINE_DOC_NAMES: tuple[str, ...] = (
    "README.md",
    "CHANGELOG.md",
    "user-guide.md",
    "technical-overview.md",
    "dev-packaging.md",
)


@dataclass(frozen=True)
class ReleaseLayout:
    """Concrete filesystem layout for one packaged portable release.

    Attributes:
        folder_name: Top-level folder name inside the zip artifact.
        target_arch: Public target architecture label used in release asset names.
        dist_dir: Existing Nuitka standalone output directory.
        staging_dir: Temporary folder populated before zipping.
        app_dir: Target app folder inside the staged release.
        zip_path: Final release zip path.
    """

    folder_name: str
    target_arch: str
    dist_dir: Path
    staging_dir: Path
    app_dir: Path
    zip_path: Path


@dataclass(frozen=True)
class NuitkaConfig:
    """Normalized packaging settings loaded from ``pyproject.toml``."""

    app_package: str
    output_name: str
    mode: str
    windows_console_mode: str
    enable_plugins: tuple[str, ...]
    include_qt_plugins: tuple[str, ...]
    include_data_files: tuple[str, ...]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for portable release packaging."""

    parser = argparse.ArgumentParser(
        prog="package_release.py",
        description="Create the portable Windows release zip.",
    )
    parser.add_argument(
        "--release-tag",
        default="",
        help="Release tag suffix used in the artifact name, such as v0.1.1.",
    )
    parser.add_argument(
        "--target-arch",
        default="windows-x64",
        choices=("windows-x64", "windows-arm64"),
        help="Public target architecture label used in release asset names.",
    )
    return parser.parse_args(argv)


def load_project_version(repo_root: Path) -> str:
    """Return the package version declared in ``pyproject.toml``."""

    payload = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    project_section = payload.get("project")
    if not isinstance(project_section, dict):
        raise ValueError("pyproject.toml is missing the [project] table.")
    raw_version = project_section.get("version")
    if not isinstance(raw_version, str) or not raw_version.strip():
        raise ValueError("pyproject.toml is missing [project].version.")
    return raw_version.strip()


def _expect_string(value: object, field_name: str) -> str:
    """Return one string field or raise a descriptive configuration error."""

    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"tool.workspace.nuitka.{field_name} must be a non-empty string."
        )
    return value


def _expect_string_list(value: object, field_name: str) -> tuple[str, ...]:
    """Return a tuple of strings or raise a descriptive configuration error."""

    if not isinstance(value, list):
        raise ValueError(
            f"tool.workspace.nuitka.{field_name} must be a list of strings."
        )
    normalized_items: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(
                f"tool.workspace.nuitka.{field_name} must contain non-empty strings."
            )
        normalized_items.append(item)
    return tuple(normalized_items)


def load_nuitka_config(repo_root: Path) -> NuitkaConfig:
    """Load and validate Nuitka settings from ``pyproject.toml``."""

    payload = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    tool_section = payload.get("tool")
    if not isinstance(tool_section, dict):
        raise ValueError("pyproject.toml is missing the [tool] table.")

    workspace_section = tool_section.get("workspace")
    if not isinstance(workspace_section, dict):
        raise ValueError("pyproject.toml is missing the [tool.workspace] table.")

    nuitka_section = workspace_section.get("nuitka")
    if not isinstance(nuitka_section, dict):
        raise ValueError("pyproject.toml is missing the [tool.workspace.nuitka] table.")

    return NuitkaConfig(
        app_package=_expect_string(nuitka_section.get("app_package"), "app_package"),
        output_name=_expect_string(nuitka_section.get("output_name"), "output_name"),
        mode=_expect_string(nuitka_section.get("mode"), "mode"),
        windows_console_mode=_expect_string(
            nuitka_section.get("windows_console_mode"),
            "windows_console_mode",
        ),
        enable_plugins=_expect_string_list(
            nuitka_section.get("enable_plugins"),
            "enable_plugins",
        ),
        include_qt_plugins=_expect_string_list(
            nuitka_section.get("include_qt_plugins"),
            "include_qt_plugins",
        ),
        include_data_files=_expect_string_list(
            nuitka_section.get("include_data_files"),
            "include_data_files",
        ),
    )


def resolve_dist_dir(repo_root: Path, config: NuitkaConfig) -> Path:
    """Return the existing standalone output directory created by Nuitka."""

    standalone_root = repo_root / "build" / "nuitka" / config.mode
    expected_dist_dir = standalone_root / f"{config.output_name}.dist"
    if expected_dist_dir.is_dir():
        return expected_dist_dir

    dist_dirs = sorted(path for path in standalone_root.glob("*.dist") if path.is_dir())
    if len(dist_dirs) == 1:
        return dist_dirs[0]

    raise ValueError(
        "Standalone build output not found. Run "
        "'python scripts\\windows\\build_nuitka.py' first."
    )


def build_release_layout(
    repo_root: Path,
    release_tag: str,
    target_arch: str = "windows-x64",
) -> ReleaseLayout:
    """Return the concrete staging layout for one portable release package."""

    config = load_nuitka_config(repo_root)
    dist_dir = resolve_dist_dir(repo_root, config)

    folder_name = f"{config.output_name}-{target_arch}-{release_tag}"
    staging_dir = repo_root / "build" / "release" / folder_name
    app_dir = staging_dir / config.output_name
    zip_path = staging_dir.parent / f"{folder_name}.zip"
    return ReleaseLayout(
        folder_name=folder_name,
        target_arch=target_arch,
        dist_dir=dist_dir,
        staging_dir=staging_dir,
        app_dir=app_dir,
        zip_path=zip_path,
    )


def stage_release(layout: ReleaseLayout, repo_root: Path) -> None:
    """Populate the staging directory with the app folder and offline docs."""

    if layout.staging_dir.exists():
        shutil.rmtree(layout.staging_dir)
    if layout.zip_path.exists():
        layout.zip_path.unlink()

    layout.staging_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(layout.dist_dir, layout.app_dir)
    shutil.copy2(repo_root / "README.md", layout.staging_dir / "README.md")
    shutil.copy2(repo_root / "LICENSE", layout.staging_dir / "LICENSE")
    stage_offline_docs(layout, repo_root)


def stage_offline_docs(layout: ReleaseLayout, repo_root: Path) -> None:
    """Copy README-linked markdown docs into the portable release."""

    source_docs_dir = repo_root / "docs"
    target_docs_dir = layout.staging_dir / "docs"
    target_docs_dir.mkdir(parents=True, exist_ok=True)

    for doc_name in OFFLINE_DOC_NAMES:
        source_path = source_docs_dir / doc_name
        if source_path.is_file():
            shutil.copy2(source_path, target_docs_dir / doc_name)


def write_release_zip(layout: ReleaseLayout) -> None:
    """Write the final portable release zip from the staged folder tree."""

    with ZipFile(layout.zip_path, "w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(layout.staging_dir.rglob("*")):
            archive.write(path, arcname=path.relative_to(layout.staging_dir.parent))


def main(argv: list[str] | None = None) -> int:
    """Create the portable release zip from the existing standalone build."""

    repo_root = Path(__file__).resolve().parents[2]
    try:
        args = parse_args(argv)
        version = load_project_version(repo_root)
        release_tag = str(args.release_tag or "").strip() or f"v{version}"
        target_arch = str(args.target_arch or "").strip()
        layout = build_release_layout(repo_root, release_tag, target_arch)
        stage_release(layout, repo_root)
        write_release_zip(layout)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"ERROR: failed to package release: {exc}", file=sys.stderr)
        return 1

    print(f"Portable release staged at: {layout.staging_dir}")
    print(f"Portable release zip: {layout.zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
