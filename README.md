# Video Duperz

Video Duperz is a Windows desktop app for finding perceptual duplicate videos, reviewing them side by side, and deciding which copy to keep.

It is aimed at technical users with large local libraries who want a fast duplicate pass, visible scan telemetry, and detailed results before deleting anything.

## First Public Windows Release

- Primary download: single Windows executable from GitHub Releases
- Fallback download: portable GitHub Release zip
- Supported platform: Windows 10/11 x64
- The single executable is unsigned in the first automated release and may show
  a Windows SmartScreen warning
- Portable package contents:
  - `video-duperz/` app folder
  - `README.md`
  - `LICENSE`
- The release does **not** bundle the FFmpeg suite
- The app now opens even when required scan tools are missing, then explains what needs to be configured before scanning

Releases: <https://github.com/threepwood-py-labs/video-duperz/releases>

## What It Does

- Finds likely duplicate videos using perceptual hashing instead of filename matching
- Compares cross-resolution copies with configurable similarity profiles
- Uses physical-drive-aware scheduling so scans stay more efficient on multi-disk libraries
- Picks a default keep candidate using video quality signals such as resolution and bitrate
- Exports duplicate groups and tracked filesystem links to CSV and JSON
- Keeps optional integrations like Everything and MediaInfo available without making them required

## User Guide

Start with the [user guide](docs/user-guide.md) for first-run setup, scan
configuration, duplicate review workflows, delete/rename safety, and
troubleshooting.

## Requirements

### Required for scanning

- Windows 10 or Windows 11
- The single release executable, or a local extracted copy of the release zip
- The FFmpeg suite installed or manually configured
  - `ffmpeg.exe`
  - `ffprobe.exe`

### Included in the app package

- The Qt desktop app itself
- Python runtime packaged into the standalone build
- Built-in first-run tool-path discovery for common Windows installs

### Optional extras

- `MediaInfo.exe` for richer file inspection from the Results view
- `Everything.exe` for instant filename lookup from the Results view
- `fpcalc.exe` if you want audio fingerprint matching features

## Install and First Run

### 1. Download

Download the latest `video-duperz-vX.Y.Z-windows-x64.exe` from GitHub Releases
and place it in a normal writable folder, for example `C:\Tools\VideoDuperz`.

If the single executable does not work on your machine, download the portable zip
instead, extract it to the same kind of folder, and run the exe inside the
extracted `video-duperz` folder. Do not run the portable build directly from
inside the zip file.

### 2. Install the FFmpeg suite

Video Duperz does not ship FFmpeg in the first release. Install the FFmpeg suite so the app can resolve `ffmpeg.exe` and `ffprobe.exe`.

Windows package-manager examples:

```powershell
winget install Gyan.FFmpeg
```

```powershell
choco install ffmpeg
```

```powershell
scoop install ffmpeg
```

### 3. Start the app

Launch:

```text
video-duperz-vX.Y.Z-windows-x64.exe
```

For the portable zip fallback, launch `video-duperz\video-duperz.exe` from the
extracted folder.

If the app cannot find the required scan tools, it opens and shows a setup warning instead of exiting immediately.

### 4. Fix tool paths if needed

Open the **Sources** tab and use **Tool Paths** to:

- leave fields blank and use auto-discovery / PATH lookup
- click **Find** to search common install locations
- click **Browse...** to point directly at a specific executable

Scan actions remain disabled until the required scan components are available.

## Quick Start

1. Add one or more scan folders on the **Sources** tab.
2. Leave the default similarity profile on **Balanced** for the first pass.
3. Confirm the scan-readiness note says scanning is ready.
4. Open the **Scan** tab and start the scan.
5. Review duplicate groups on the **Results** tab.
6. Use keep strategies, per-row selection, and delete actions carefully.
7. Export the current scan if you want an external review before cleanup.

## Optional Extras

These integrations are useful, but not required for the first release:

- **MediaInfo**: launch richer media inspection for the current file
- **Everything**: search the current filename instantly
- **fpcalc**: enable audio fingerprint matching workflows

If those tools are missing, Video Duperz still launches and scans normally. Only the related feature entry points stay unavailable.

## Troubleshooting

### The app opens, but scan buttons are disabled

The required scan tools are not ready yet.

Check:

- `ffmpeg.exe` is installed
- `ffprobe.exe` is installed
- the configured override paths are valid
- the **Probe Backend** and tool-path settings match what is installed

### I installed FFmpeg, but the app still cannot find it

Use **Sources > Tool Paths**:

- click **Find** first
- if that still fails, click **Browse...** and select the exact executable path

### The app should work without ffprobe because I use the PyAV backend

The release documentation still recommends installing the full FFmpeg suite because it gives the smoothest Windows setup and keeps both `ffmpeg` and `ffprobe` available when you need them.

### I want to reset everything

Use **File > Full Reset** to clear the app database, cached thumbnails, and saved settings.

## Known Limitations

- First public release is Windows-only
- First public release is portable-only; there is no installer yet
- FFmpeg is not bundled in the first release
- Large scans can still be I/O-heavy, especially on slower disks
- Results should be reviewed before destructive delete actions

## Technical Docs

- [Documentation Index](docs/README.md)
- [User Guide](docs/user-guide.md)
- [Technical Overview](docs/technical-overview.md)
- [Packaging and Release Notes](docs/dev-packaging.md)

## Development

For local development:

```powershell
python scripts/windows/setup_env.py
```

```powershell
hatch run test
```

```powershell
hatch run lint:check
```

```powershell
hatch run package:standalone
```

## License

MIT. See [LICENSE](LICENSE).

<!-- legal-disclaimer:start -->
## Legal Disclaimer

THIS SOFTWARE IS PROVIDED "AS IS" AND "AS AVAILABLE," WITHOUT WARRANTIES OF ANY KIND, WHETHER EXPRESS, IMPLIED, STATUTORY, OR OTHERWISE, INCLUDING, WITHOUT LIMITATION, ANY IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE, NON-INFRINGEMENT, ACCURACY, OR QUIET ENJOYMENT. TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, THE AUTHORS, CONTRIBUTORS, MAINTAINERS, DISTRIBUTORS, AND AFFILIATED PARTIES SHALL NOT BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, EXEMPLARY, OR PUNITIVE DAMAGES, OR FOR ANY LOSS OF DATA, PROFITS, GOODWILL, BUSINESS OPPORTUNITY, OR SERVICE INTERRUPTION, ARISING OUT OF OR RELATING TO THE USE OF, OR INABILITY TO USE, THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES. THIS SOFTWARE HAS BEEN DEVELOPED, IN WHOLE OR IN PART, BY "INTELLIGENT TOOLS"; ACCORDINGLY, OUTPUTS MAY CONTAIN ERRORS OR OMISSIONS, AND YOU ASSUME FULL RESPONSIBILITY FOR INDEPENDENT VALIDATION, TESTING, LEGAL COMPLIANCE, AND SAFE OPERATION PRIOR TO ANY RELIANCE OR DEPLOYMENT.
<!-- legal-disclaimer:end -->
