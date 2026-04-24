"""Unit tests for scan runtime readiness checks."""

from __future__ import annotations

from video_duperz.config import default_settings
from video_duperz.fingerprint import FingerprintError
from video_duperz.probe import ProbeError
from video_duperz.scan_readiness import evaluate_scan_readiness


def test_scan_readiness_is_ready_when_dependencies_are_available(
    monkeypatch,
) -> None:
    """Return a ready status when both runtime checks succeed."""

    monkeypatch.setattr(
        "video_duperz.scan_readiness.ensure_probe_backend_available",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "video_duperz.scan_readiness.ensure_fingerprint_fallback_chain_available",
        lambda *_args, **_kwargs: None,
    )

    readiness = evaluate_scan_readiness(default_settings())

    assert readiness.is_ready is True
    assert readiness.summary == "Scan readiness: ready."
    assert readiness.issues == ()


def test_scan_readiness_reports_missing_ffmpeg_and_ffprobe(monkeypatch) -> None:
    """Describe the missing FFmpeg suite components when both checks fail."""

    def _missing_probe(*_args, **_kwargs) -> None:
        raise ProbeError(
            "ffprobe not found on PATH. Install ffmpeg and add it to PATH."
        )

    def _missing_fingerprint(*_args, **_kwargs) -> None:
        raise FingerprintError(
            "ffmpeg not found on PATH. Install ffmpeg and add it to PATH."
        )

    monkeypatch.setattr(
        "video_duperz.scan_readiness.ensure_probe_backend_available",
        _missing_probe,
    )
    monkeypatch.setattr(
        "video_duperz.scan_readiness.ensure_fingerprint_fallback_chain_available",
        _missing_fingerprint,
    )

    settings = default_settings()
    settings.probe_backend = "ffprobe"
    readiness = evaluate_scan_readiness(settings)

    assert readiness.is_ready is False
    assert "ffprobe" in readiness.summary
    assert "ffmpeg" in readiness.summary
    assert "Install the FFmpeg suite" in readiness.guidance
    assert "scanning is not ready yet" in readiness.modal_text()


def test_scan_readiness_reports_pyav_specific_guidance(monkeypatch) -> None:
    """Suggest a repair path when the packaged PyAV runtime is unavailable."""

    def _missing_probe(*_args, **_kwargs) -> None:
        raise ProbeError("PyAV backend is unavailable.")

    monkeypatch.setattr(
        "video_duperz.scan_readiness.ensure_probe_backend_available",
        _missing_probe,
    )
    monkeypatch.setattr(
        "video_duperz.scan_readiness.ensure_fingerprint_fallback_chain_available",
        lambda *_args, **_kwargs: None,
    )

    readiness = evaluate_scan_readiness(default_settings())

    assert readiness.is_ready is False
    assert readiness.issues[0].component == "PyAV"
    assert "switch the probe backend to ffprobe" in readiness.guidance
