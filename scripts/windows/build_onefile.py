"""Build a Windows Nuitka onefile executable from the local interpreter."""

from __future__ import annotations

import subprocess
import sys
import tomllib
from dataclasses import replace
from pathlib import Path

from _common import ensure_package_dependencies, ensure_venv, get_python
from build_nuitka import NuitkaConfig, build_command, load_nuitka_config


def load_onefile_nuitka_config(repo_root: Path) -> NuitkaConfig:
    """Load Nuitka config and force onefile mode for the executable asset."""

    return replace(load_nuitka_config(repo_root), mode="onefile")


def main() -> int:
    """Build the configured app as a single onefile executable."""

    repo_root = Path(__file__).resolve().parents[2]
    rc = ensure_venv(repo_root)
    if rc != 0:
        return rc

    rc = ensure_package_dependencies(repo_root)
    if rc != 0:
        return rc

    python_exe = get_python(repo_root)
    if not python_exe.exists():
        print(
            "ERROR: local interpreter not found at .venv\\Scripts\\python.exe.",
            file=sys.stderr,
        )
        print("Run: python scripts\\windows\\setup_env.py", file=sys.stderr)
        return 1

    try:
        config = load_onefile_nuitka_config(repo_root)
        command, environment = build_command(repo_root, config, sys.argv[1:])
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"ERROR: failed to prepare Nuitka onefile build: {exc}", file=sys.stderr)
        return 1

    print("Running Nuitka onefile build:")
    print(" ".join(command))
    return subprocess.run(
        command,
        cwd=repo_root,
        check=False,
        env=environment,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
