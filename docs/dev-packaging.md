# Packaging and Release Notes

## Current Release Shape

- Product: `video-duperz`
- Public release line: `v0.1.3`
- Primary artifact: single Windows executable
- Fallback artifact: portable Windows zip
- Supported targets: Windows 10/11 x64 and Windows 11 ARM64
- The single executable is unsigned in the first automated release and may show
  a Windows SmartScreen warning
- Portable zip contents:
  - packaged standalone app folder
  - `README.md`
  - `LICENSE`
  - `docs/` markdown files referenced by the README

The first public release does not include an installer and does not bundle the FFmpeg suite.

## Local Build Commands

Prepare the local environment:

```powershell
python scripts/windows/setup_env.py
```

Build the standalone executable:

```powershell
python scripts/windows/build_nuitka.py
```

Package the public release zip:

```powershell
python scripts/windows/package_release.py --release-tag v0.1.3 --target-arch windows-x64
```

Build the onefile executable:

```powershell
python scripts/windows/build_onefile.py
```

Stage the public onefile executable:

```powershell
python scripts/windows/package_onefile.py --release-tag v0.1.3 --target-arch windows-x64
```

Write public release checksums:

```powershell
python scripts/windows/write_release_checksums.py
```

Equivalent Hatch entry point:

```powershell
hatch run package:package-release --release-tag v0.1.3 --target-arch windows-x64
hatch run package:onefile
hatch run package:package-onefile --release-tag v0.1.3 --target-arch windows-x64
hatch run package:checksums
```

## Output Layout

Expected build outputs:

- standalone app folder:
  - `build/nuitka/standalone/video-duperz.dist`
- onefile executable:
  - `build/nuitka/onefile/video-duperz.exe`
- staged portable release:
  - `build/release/video-duperz-windows-x64-v0.1.3`
- release zip:
  - `build/release/video-duperz-windows-x64-v0.1.3.zip`
- public onefile executable:
  - `build/release/video-duperz-v0.1.3-windows-x64.exe`
- ARM64 release assets use the same naming pattern with `windows-arm64`
  replacing `windows-x64`.
- checksums:
  - `build/release/SHA256SUMS.txt`

## GitHub Release Workflow

The repo includes an automated Windows release workflow:

- workflow file: `.github/workflows/release.yml`
- triggers: tag push matching `v*.*.*`, or manual `workflow_dispatch`
- behavior:
  - validates the release tag matches `pyproject.toml`
  - builds x64 assets on the GitHub-hosted `windows-latest` runner
  - builds ARM64 assets on the GitHub-hosted `windows-11-arm` runner
  - builds standalone executables and portable zips
  - builds onefile executables
  - smoke-tests the public onefile executable with `--help`
  - uploads per-architecture release assets as workflow artifacts
  - writes one combined `SHA256SUMS.txt`
  - attests all public release assets and checksums
  - uploads combined release assets as a workflow artifact
  - creates or updates one GitHub Release with both architectures

Recommended first-release flow:

1. Run the workflow manually with `draft_release = true`.
2. Download and validate the exe, zip, and checksums.
3. Push the matching `v0.1.3` tag once the result is correct.

## Validation Checklist

Before publishing a release:

- `hatch run lint:check`
- `hatch run lint:fmt`
- `hatch run lint:types`
- `hatch run lint:deps`
- `hatch run lint:policy`
- `hatch run test`
- onefile executable prints help with `--help`
- onefile executable launches on Windows
- portable standalone app launches on Windows
- startup warning appears when required scan tools are unavailable
- scan buttons enable correctly once required tools are configured
- release assets contain:
  - `video-duperz-v0.1.3-windows-x64.exe`
  - `video-duperz-v0.1.3-windows-arm64.exe`
  - `video-duperz-windows-x64-v0.1.3.zip`
  - `video-duperz-windows-arm64-v0.1.3.zip`
  - `SHA256SUMS.txt`
- release zip contains:
  - app folder
  - `README.md`
  - `LICENSE`
  - README-linked docs under `docs/`

## Release Notes Style

Keep first-release notes user-facing:

- what Video Duperz does
- what is included in the portable package
- required setup for the FFmpeg suite
- any known limitations for the current cut

Avoid turning first-release notes into an internal changelog.
