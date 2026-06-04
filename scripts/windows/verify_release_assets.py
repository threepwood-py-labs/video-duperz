"""Verify public release assets and their SHA256 checksums."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

TARGET_ARCHES = ("windows-x64", "windows-arm64")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for release asset verification."""

    parser = argparse.ArgumentParser(
        prog="verify_release_assets.py",
        description="Verify release asset names and SHA256SUMS.txt contents.",
    )
    parser.add_argument(
        "--release-dir",
        default="build/release",
        help="Directory containing public release assets.",
    )
    parser.add_argument(
        "--release-tag",
        required=True,
        help="Release tag used in public asset names, such as v0.1.4.",
    )
    parser.add_argument(
        "--target-arch",
        action="append",
        choices=TARGET_ARCHES,
        dest="target_arches",
        help="Expected public target architecture. Defaults to all release arches.",
    )
    return parser.parse_args(argv)


def expected_asset_names(
    release_tag: str,
    target_arches: tuple[str, ...],
) -> tuple[str, ...]:
    """Return the complete expected executable and zip asset names."""

    names: list[str] = []
    for target_arch in target_arches:
        names.append(f"video-duperz-{release_tag}-{target_arch}.exe")
        names.append(f"video-duperz-{target_arch}-{release_tag}.zip")
    return tuple(sorted(names, key=str.lower))


def release_asset_names(release_dir: Path) -> tuple[str, ...]:
    """Return public executable and zip asset names found in the release directory."""

    names: list[str] = []
    for pattern in ("*.exe", "*.zip"):
        names.extend(path.name for path in release_dir.glob(pattern) if path.is_file())
    return tuple(sorted(names, key=str.lower))


def sha256_file(path: Path) -> str:
    """Return the hex SHA256 digest for one file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_checksum_file(checksum_path: Path) -> dict[str, str]:
    """Return filename-to-digest mappings from a SHA256SUMS.txt file."""

    checksums: dict[str, str] = {}
    for line_number, raw_line in enumerate(
        checksum_path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            raise ValueError(
                f"Invalid checksum line {line_number} in {checksum_path.name}."
            )
        digest, filename = parts
        if len(digest) != 64:
            raise ValueError(
                f"Invalid SHA256 digest for {filename!r} in {checksum_path.name}."
            )
        checksums[filename.strip()] = digest.lower()
    return checksums


def _format_name_set(names: set[str]) -> str:
    """Format a deterministic comma-separated file list for error messages."""

    return ", ".join(sorted(names, key=str.lower))


def verify_release_assets(
    release_dir: Path,
    release_tag: str,
    target_arches: tuple[str, ...] = TARGET_ARCHES,
) -> None:
    """Verify the public release asset set and checksums."""

    if not release_dir.exists():
        raise ValueError(f"Release directory does not exist: {release_dir}")

    expected_names = set(expected_asset_names(release_tag, target_arches))
    actual_names = set(release_asset_names(release_dir))
    missing = expected_names - actual_names
    unexpected = actual_names - expected_names
    if missing:
        raise ValueError(f"Missing release assets: {_format_name_set(missing)}")
    if unexpected:
        raise ValueError(f"Unexpected release assets: {_format_name_set(unexpected)}")

    checksum_path = release_dir / "SHA256SUMS.txt"
    if not checksum_path.is_file():
        raise ValueError(f"Missing release checksum file: {checksum_path}")

    checksums = parse_checksum_file(checksum_path)
    checksum_names = set(checksums)
    missing_checksums = expected_names - checksum_names
    unexpected_checksums = checksum_names - expected_names
    if missing_checksums:
        raise ValueError(f"Missing checksums: {_format_name_set(missing_checksums)}")
    if unexpected_checksums:
        raise ValueError(
            f"Unexpected checksum entries: {_format_name_set(unexpected_checksums)}"
        )

    mismatched: list[str] = []
    for asset_name in sorted(expected_names, key=str.lower):
        asset_path = release_dir / asset_name
        if sha256_file(asset_path) != checksums[asset_name]:
            mismatched.append(asset_name)
    if mismatched:
        raise ValueError(f"Checksum mismatch: {_format_name_set(set(mismatched))}")


def main(argv: list[str] | None = None) -> int:
    """Verify release assets and return a process exit code."""

    repo_root = Path(__file__).resolve().parents[2]
    args = parse_args(argv)
    release_dir = (repo_root / str(args.release_dir)).resolve()
    target_arches = tuple(args.target_arches or TARGET_ARCHES)
    release_tag = str(args.release_tag).strip()
    try:
        verify_release_assets(release_dir, release_tag, target_arches)
    except (OSError, ValueError) as exc:
        print(f"ERROR: failed to verify release assets: {exc}", file=sys.stderr)
        return 1

    print(f"Verified release assets in: {release_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
