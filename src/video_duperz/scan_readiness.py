"""Scan runtime readiness checks used by the GUI and release builds."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .fingerprint import FingerprintError, ensure_fingerprint_fallback_chain_available
from .probe import ProbeError, ensure_probe_backend_available

if TYPE_CHECKING:
    from .models import ProbeBackendId, Settings


@dataclass(frozen=True)
class ScanReadinessIssue:
    """One user-facing problem that blocks scan execution.

    Attributes:
        component: Human-facing component or tool name.
        message: Concrete resolution message shown to the user.
    """

    component: str
    message: str


@dataclass(frozen=True)
class ScanReadiness:
    """Normalized scan readiness result for the current settings.

    Attributes:
        is_ready: Whether scan execution can start safely.
        summary: Short status text suitable for inline UI.
        guidance: Short actionable guidance suitable for labels and tooltips.
        issues: Blocking problems collected during validation.
    """

    is_ready: bool
    summary: str
    guidance: str
    issues: tuple[ScanReadinessIssue, ...]

    def details_text(self) -> str:
        """Return one multi-line diagnostic string for tooltips and logs."""

        if self.is_ready:
            return self.summary
        issue_lines = [f"- {issue.component}: {issue.message}" for issue in self.issues]
        return "\n".join([self.summary, *issue_lines, "", self.guidance])

    def modal_text(self) -> str:
        """Return one startup-warning message for missing scan requirements."""

        if self.is_ready:
            return self.summary
        issue_lines = [f"- {issue.component}: {issue.message}" for issue in self.issues]
        return "\n".join(
            [
                "Video Duperz opened, but scanning is not ready yet.",
                "",
                *issue_lines,
                "",
                self.guidance,
                (
                    "Scan actions stay disabled until the required components "
                    "are available."
                ),
            ]
        )


def evaluate_scan_readiness(settings: Settings) -> ScanReadiness:
    """Return the scan-readiness status for the provided settings.

    Args:
        settings: Current persisted or in-flight UI settings.

    Returns:
        One normalized readiness result used by the UI and tests.
    """

    issues: list[ScanReadinessIssue] = []
    seen_issue_keys: set[tuple[str, str]] = set()

    def add_issue(component: str, message: str) -> None:
        issue = ScanReadinessIssue(component=component, message=message)
        key = (issue.component.casefold(), issue.message.casefold())
        if key in seen_issue_keys:
            return
        seen_issue_keys.add(key)
        issues.append(issue)

    try:
        ensure_probe_backend_available(
            _probe_backend(settings),
            ffprobe_exe_path=str(settings.ffprobe_exe_path or ""),
        )
    except ProbeError as exc:
        probe_component = "ffprobe" if _probe_backend(settings) == "ffprobe" else "PyAV"
        add_issue(probe_component, str(exc))

    try:
        ensure_fingerprint_fallback_chain_available(str(settings.ffmpeg_exe_path or ""))
    except FingerprintError as exc:
        message = str(exc)
        component = (
            "ffmpeg" if "ffmpeg" in message.casefold() else "Fingerprint runtime"
        )
        add_issue(component, message)

    if not issues:
        return ScanReadiness(
            is_ready=True,
            summary="Scan readiness: ready.",
            guidance="Required scan components are available.",
            issues=(),
        )

    missing_components = ", ".join(issue.component for issue in issues)
    guidance = (
        "Install the FFmpeg suite or set the executable overrides in "
        "Sources > Tool Paths before starting a scan."
    )
    if all(issue.component == "PyAV" for issue in issues):
        guidance = (
            "Repair the Video Duperz install or switch the probe backend to ffprobe "
            "after configuring the FFmpeg suite."
        )
    return ScanReadiness(
        is_ready=False,
        summary=f"Scan readiness: unavailable ({missing_components}).",
        guidance=guidance,
        issues=tuple(issues),
    )


def _probe_backend(settings: Settings) -> ProbeBackendId:
    """Return one normalized probe backend from the current settings."""

    if str(settings.probe_backend or "").strip().lower() == "ffprobe":
        return "ffprobe"
    return "pyav"
