"""Stage the public onefile executable release asset."""

from __future__ import annotations

import argparse
import shutil
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

from package_release import load_nuitka_config, load_project_version


@dataclass(frozen=True)
class OnefileLayout:
    """Concrete filesystem layout for one onefile executable release asset.

    Attributes:
        source_exe: Existing Nuitka onefile executable.
        release_exe: Public release executable path.
    """

    source_exe: Path
    release_exe: Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for onefile release packaging."""

    parser = argparse.ArgumentParser(
        prog="package_onefile.py",
        description="Stage the public Windows onefile executable.",
    )
    parser.add_argument(
        "--release-tag",
        default="",
        help="Release tag suffix used in the artifact name, such as v0.1.1.",
    )
    return parser.parse_args(argv)


def resolve_onefile_exe(repo_root: Path) -> Path:
    """Return the existing onefile executable created by Nuitka."""

    config = load_nuitka_config(repo_root)
    onefile_root = repo_root / "build" / "nuitka" / "onefile"
    expected_exe = onefile_root / f"{config.output_name}.exe"
    if expected_exe.is_file():
        return expected_exe

    exe_files = sorted(path for path in onefile_root.glob("*.exe") if path.is_file())
    if len(exe_files) == 1:
        return exe_files[0]

    raise ValueError(
        "Onefile build output not found. Run "
        "'python scripts\\windows\\build_onefile.py' first."
    )


def build_onefile_layout(repo_root: Path, release_tag: str) -> OnefileLayout:
    """Return the concrete source and public onefile executable paths."""

    config = load_nuitka_config(repo_root)
    source_exe = resolve_onefile_exe(repo_root)
    release_dir = repo_root / "build" / "release"
    release_exe = release_dir / f"{config.output_name}-{release_tag}-windows-x64.exe"
    return OnefileLayout(source_exe=source_exe, release_exe=release_exe)


def stage_onefile(layout: OnefileLayout) -> None:
    """Copy the onefile executable to its public release asset path."""

    layout.release_exe.parent.mkdir(parents=True, exist_ok=True)
    if layout.release_exe.exists():
        layout.release_exe.unlink()
    shutil.copy2(layout.source_exe, layout.release_exe)


def main(argv: list[str] | None = None) -> int:
    """Stage the public onefile executable release asset."""

    repo_root = Path(__file__).resolve().parents[2]
    try:
        args = parse_args(argv)
        version = load_project_version(repo_root)
        release_tag = str(args.release_tag or "").strip() or f"v{version}"
        layout = build_onefile_layout(repo_root, release_tag)
        stage_onefile(layout)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"ERROR: failed to package onefile executable: {exc}", file=sys.stderr)
        return 1

    print(f"Onefile executable: {layout.release_exe}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
