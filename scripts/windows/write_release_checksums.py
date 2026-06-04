"""Write SHA256 checksums for public release assets."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for checksum generation."""

    parser = argparse.ArgumentParser(
        prog="write_release_checksums.py",
        description="Write SHA256SUMS.txt for release assets.",
    )
    parser.add_argument(
        "--release-dir",
        default="build/release",
        help="Directory containing public release assets.",
    )
    return parser.parse_args(argv)


def release_asset_paths(release_dir: Path) -> tuple[Path, ...]:
    """Return release asset files that should be included in SHA256SUMS.txt."""

    patterns = ("*.exe", "*.zip")
    paths: list[Path] = []
    for pattern in patterns:
        paths.extend(path for path in release_dir.glob(pattern) if path.is_file())
    return tuple(sorted(paths, key=lambda path: path.name.lower()))


def sha256_file(path: Path) -> str:
    """Return the hex SHA256 digest for one file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_checksums(release_dir: Path) -> Path:
    """Write ``SHA256SUMS.txt`` and return its path."""

    assets = release_asset_paths(release_dir)
    if not assets:
        raise ValueError(f"No .exe or .zip release assets found in {release_dir}.")

    checksum_path = release_dir / "SHA256SUMS.txt"
    lines = [f"{sha256_file(path)}  {path.name}" for path in assets]
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return checksum_path


def main(argv: list[str] | None = None) -> int:
    """Write release asset checksums."""

    repo_root = Path(__file__).resolve().parents[2]
    args = parse_args(argv)
    release_dir = (repo_root / str(args.release_dir)).resolve()
    try:
        checksum_path = write_checksums(release_dir)
    except (OSError, ValueError) as exc:
        print(f"ERROR: failed to write release checksums: {exc}", file=sys.stderr)
        return 1

    print(f"Release checksums: {checksum_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
