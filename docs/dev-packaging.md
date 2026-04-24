# Packaging and Release Notes

## Current Release Shape

- Product: `video-duperz`
- Public release line: `r-0.1.1`
- Primary artifact: portable Windows zip
- Supported target: Windows 10/11 x64
- Portable zip contents:
  - packaged standalone app folder
  - `README.md`
  - `LICENSE`

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
python scripts/windows/package_release.py --release-tag r-0.1.1
```

Equivalent Hatch entry point:

```powershell
hatch run package:package-release --release-tag r-0.1.1
```

## Output Layout

Expected build outputs:

- standalone app folder:
  - `build/nuitka/standalone/video-duperz.dist`
- staged portable release:
  - `build/release/video-duperz-windows-x64-r-0.1.1`
- release zip:
  - `build/release/video-duperz-windows-x64-r-0.1.1.zip`

## GitHub Release Workflow

The repo includes a manual Windows release workflow:

- workflow file: `.github/workflows/release.yml`
- trigger: `workflow_dispatch`
- behavior:
  - builds the standalone executable
  - packages the portable zip
  - uploads the zip as a workflow artifact
  - optionally creates a draft GitHub Release

Recommended first-release flow:

1. Run the workflow manually with `publish_release = false`.
2. Download and validate the artifact.
3. Re-run with `publish_release = true` once the result is correct.

## Validation Checklist

Before publishing a release:

- `hatch run lint:check`
- `hatch run lint:fmt`
- `hatch run lint:types`
- `hatch run lint:deps`
- `hatch run lint:policy`
- `hatch run test`
- standalone app launches on Windows
- startup warning appears when required scan tools are unavailable
- scan buttons enable correctly once required tools are configured
- release zip contains:
  - app folder
  - `README.md`
  - `LICENSE`

## Release Notes Style

Keep first-release notes user-facing:

- what Video Duperz does
- what is included in the portable package
- required setup for the FFmpeg suite
- any known limitations for the current cut

Avoid turning first-release notes into an internal changelog.
