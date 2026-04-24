# Technical Overview

## Product Shape

Video Duperz is a PySide6 desktop application with a `src/` layout and a single top-level package: `video_duperz`.

Primary entry points:

- GUI: `python -m video_duperz gui`
- headless scan: `python -m video_duperz scan`
- export: `python -m video_duperz export`
- full reset: `python -m video_duperz clean --full-reset`

The packaged Windows release uses Nuitka standalone mode.

## Main Runtime Pieces

- `config.py`
  - QSettings defaults, persistence, first-run executable discovery
- `db.py`
  - SQLite storage for scans, artifacts, duplicate groups, and exports
- `scanner.py`
  - file discovery and physical-drive mapping
- `pipeline.py` and `pipeline_runtime.py`
  - scan orchestration and persisted resume behavior
- `probe.py`
  - metadata extraction backends
- `fingerprint.py`
  - visual fingerprint generation and decoder fallback handling
- `matcher.py`
  - candidate comparison and duplicate grouping
- `quality.py`
  - default keep-choice scoring
- `ui/`
  - main window, scan telemetry, results table, thumbnail and worker UI logic

## Scan Pipeline

High-level scan flow:

1. enumerate files under selected roots
2. map work to physical-drive-aware lanes
3. reuse valid cached artifacts where possible
4. probe metadata for files that still need analysis
5. fingerprint visual content
6. compare plausible candidates under the selected similarity profile
7. group duplicate edges
8. pick a default keep candidate for each group

Resume behavior is persistence-based, not thread-suspension based. A resumed scan re-enumerates current files, reloads valid cached artifacts, and skips unchanged work.

## Matching Model

Video Duperz does not depend on filenames for duplicate detection.

It combines:

- metadata-driven candidate narrowing
- sampled visual hashing
- configurable similarity thresholds

Current built-in profiles:

- `conservative`
- `balanced`
- `aggressive`

The final keep suggestion is weighted toward:

- resolution
- bitrate
- codec quality

## Probe and Decode Backends

### Probe backend

Metadata extraction can use:

- `pyav`
- `ffprobe`

The selected probe backend is part of cache validity.

### Fingerprint decode path

Fingerprint frame extraction can use:

- `opencv`
- `pyav`
- `ffmpeg`

The runtime uses fallback logic for difficult formats, with `ffmpeg` available as the guarded external decoder path.

## Settings and Data

The app stores:

- settings in QSettings INI form
- runtime data under the app data directory
- SQLite scan data and caches in the local app data tree

The first public release now uses the `itlezy` app identity.

## Packaging Notes

The repo keeps packaging logic in `scripts/windows/`:

- `setup_env.py`
  - prepares the local `.venv`
- `build_nuitka.py`
  - builds the standalone app from the local interpreter
- `package_release.py`
  - assembles the public portable zip

The GitHub release workflow is intentionally manual-first so the first public release can be validated before publishing.
