# User Guide

## Product Scope

Video Duperz is a Windows desktop app for finding likely duplicate videos by comparing media metadata and perceptual fingerprints. It is designed for technical users who want visible scan telemetry, reviewable duplicate groups, and cautious cleanup workflows.

The first public package is portable-only. It does not include the FFmpeg suite.

## Install and First Run

1. Download and extract the portable package to a writable folder.
2. Install the FFmpeg suite so `ffmpeg.exe` and `ffprobe.exe` are available.
3. Start the app:

```text
video-duperz\video-duperz.exe
```

4. If startup reports missing scan tools, open the Sources tab and configure tool paths.
5. Confirm scan readiness before starting a scan.

For source/development runs, use:

```powershell
python scripts/windows/setup_env.py
```

```powershell
python -m video_duperz gui
```

## Configure Scan Sources

Prepare:

- one or more local scan roots
- a similarity profile
- optional minimum and maximum size limits
- tool paths for FFmpeg/ffprobe when auto-discovery does not find them
- optional paths for MediaInfo, Everything, or fpcalc

Start with a small folder before scanning a full library. This validates tool paths, permissions, and expected duplicate grouping behavior.

## Daily Scan Workflow

1. Open the Sources tab.
2. Add scan roots.
3. Confirm tool readiness.
4. Pick the similarity profile:
   - Conservative for fewer false positives.
   - Balanced for normal review.
   - Aggressive for broader candidate discovery.
5. Start the scan from the Scan tab.
6. Watch progress, active lanes, issue counts, and throughput.
7. Review groups in the Results tab.
8. Export results before taking destructive actions on a large library.

## Review Workflow

1. Sort duplicate groups by size saved, confidence, or review priority.
2. Inspect each group before acting.
3. Compare resolution, bitrate, duration, codec, path, and file size.
4. Use the suggested keep item as a starting point, not as an automatic decision.
5. Open files externally when metadata is not enough.
6. Apply delete or rename actions only after the group selection is clear.

## Common Tasks

### Scan a New Folder

Add the folder on the Sources tab, keep the Balanced profile, and run the scan. Review scan issues before judging the result set.

### Compare Cross-Resolution Copies

Enable the appropriate cross-resolution mode and use a conservative or balanced profile first. Review duration and visual similarity carefully before deleting lower-resolution copies.

### Resume or Rerun a Scan

Rerun the scan when files change. Cached metadata and fingerprints are reused when file size and timestamps still match.

### Export Results

Export duplicate groups to CSV or JSON before cleanup. Keep the export with your review notes if you are cleaning a large library in phases.

### Reset State

Use full reset only when you want to remove app database state, thumbnails, and saved settings. Export any scan results you still need first.

## Optional Integrations

- MediaInfo: richer file inspection from the Results view.
- Everything: instant filename lookup from the Results view.
- fpcalc: audio fingerprint matching workflows.

Missing optional tools do not block normal visual duplicate scans. Missing required scan tools disable scan actions until fixed.

## Settings and Data

Video Duperz stores settings, scan database state, thumbnails, and cached artifacts outside the source tree. The cache is used to avoid repeating expensive probe and fingerprint work.

If results look stale, rerun the scan after confirming the source files still exist. Use full reset only after simpler checks fail.

## Safety Notes

- Duplicate detection is probabilistic; review before deleting.
- Similarity thresholds can produce false positives.
- Large scans can be I/O-heavy.
- Delete and rename actions affect real files.
- Export results before major cleanup.
- Do not run directly from inside the zip file.

## Troubleshooting Checklist

- If scan buttons are disabled, verify `ffmpeg.exe` and `ffprobe.exe` paths.
- If the app launches but tools are missing, use Sources > Tool Paths.
- If scans are slow, reduce roots, size range, or concurrent work before scanning a full library.
- If groups look wrong, switch to a more conservative profile and rerun a smaller folder.
- If optional actions are disabled, verify MediaInfo, Everything, or fpcalc paths.
- If reset is needed, use File > Full Reset and then reconfigure tool paths.

## Getting Help

When filing an issue, include:

- app version
- Windows version
- whether you used the portable package or source install
- configured probe and decode backend
- whether FFmpeg/ffprobe were auto-discovered or manually configured
- scan profile and cross-resolution mode
- a sanitized description of the file types and folder layout
- relevant logs, scan issue text, or console output
