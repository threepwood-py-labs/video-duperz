"""GUI tests for scan-readiness messaging and blocked scan actions."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

from video_duperz.config import default_settings
from video_duperz.db import Database
from video_duperz.scan_readiness import ScanReadiness, ScanReadinessIssue
from video_duperz.ui.main_window import MainWindow

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QMessageBox

if TYPE_CHECKING:
    from pathlib import Path


def _blocked_scan_readiness() -> ScanReadiness:
    """Return one consistent blocked-scan status for UI tests."""

    return ScanReadiness(
        is_ready=False,
        summary="Scan readiness: unavailable (ffmpeg).",
        guidance=(
            "Install the FFmpeg suite or set the executable overrides in "
            "Sources > Tool Paths before starting a scan."
        ),
        issues=(
            ScanReadinessIssue(
                component="ffmpeg",
                message="ffmpeg not found on PATH. Install ffmpeg and add it to PATH.",
            ),
        ),
    )


def test_main_window_disables_scan_actions_when_scan_is_not_ready(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Disable scan actions and show guidance when requirements are missing."""

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    monkeypatch.setattr(
        "video_duperz.ui.main_window_settings.evaluate_scan_readiness",
        lambda _settings: _blocked_scan_readiness(),
    )

    with Database(tmp_path / "app.db") as db:
        settings = default_settings()
        settings.scan_roots = [str(tmp_path)]
        window = MainWindow(db=db, settings=settings)
        window.show()
        app.processEvents()

        assert window.scan_view.start_btn.isEnabled() is False
        assert window.scan_view.rescan_btn.isEnabled() is False
        assert window.scan_view.readiness_label.isHidden() is False
        assert "Install the FFmpeg suite" in window.scan_view.readiness_label.text()
        assert "ffmpeg not found on PATH" in window.scan_readiness_label.text()
        window.close()


def test_startup_scan_readiness_warning_only_shows_once(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Show the startup warning once even when called repeatedly."""

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    monkeypatch.setattr(
        "video_duperz.ui.main_window_settings.evaluate_scan_readiness",
        lambda _settings: _blocked_scan_readiness(),
    )
    warning_calls: list[tuple[str, str]] = []

    def _capture_warning(
        _parent,
        title: str,
        text: str,
        *_args,
        **_kwargs,
    ) -> QMessageBox.StandardButton:
        warning_calls.append((title, text))
        return QMessageBox.StandardButton.Ok

    monkeypatch.setattr(
        "video_duperz.ui.main_window_settings.QMessageBox.warning",
        _capture_warning,
    )

    with Database(tmp_path / "app.db") as db:
        settings = default_settings()
        settings.scan_roots = [str(tmp_path)]
        window = MainWindow(db=db, settings=settings)
        window.show()
        app.processEvents()

        window.show_startup_scan_readiness_warning_if_needed()
        window.show_startup_scan_readiness_warning_if_needed()

        assert len(warning_calls) == 1
        assert warning_calls[0][0] == "Scan Setup Required"
        assert "scanning is not ready yet" in warning_calls[0][1]
        window.close()
