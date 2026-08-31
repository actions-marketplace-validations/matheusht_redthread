"""Tests for default `redthread run` report persistence and help tiers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from click.testing import CliRunner

from redthread.cli import main
from redthread.models import CampaignConfig, CampaignResult


def _patch_fake_engine(monkeypatch: Any, runtime_mode: str = "live_provider") -> None:
    class FakeEngine:
        def __init__(self, settings: object, trace_all: bool = False) -> None:
            pass

        async def run(self, config: CampaignConfig) -> CampaignResult:
            return CampaignResult(config=config, metadata={"runtime_mode": runtime_mode})

    monkeypatch.setattr("redthread.cli.run.RedThreadEngine", FakeEngine)


def test_run_writes_default_report_directory(monkeypatch: Any, tmp_path: Path) -> None:
    _patch_fake_engine(monkeypatch)
    monkeypatch.setenv("REDTHREAD_DRY_RUN", "false")
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, ["run"])
        manifest_path = next(Path("reports").glob("*/manifest.json"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert manifest["artifact_dir"].startswith("reports/campaign-")
    assert manifest["markdown_report"].endswith("operator-report.md")
    assert "Campaign ID" in result.output
    assert "Runtime Mode" in result.output
    assert "Evidence" in result.output
    assert "Report" in result.output


def test_run_writes_default_dry_run_report_subdirectory(
    monkeypatch: Any,
    tmp_path: Path,
) -> None:
    _patch_fake_engine(monkeypatch, runtime_mode="sealed_dry_run")
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, ["run", "--dry-run"])
        manifest_path = next(Path("reports").glob("*/dry-run/manifest.json"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert manifest["artifact_dir"].endswith("/dry-run")
    assert "sealed_dry_run" in result.output
    assert "dry-run" in result.output


def test_run_report_dir_overrides_default_root(monkeypatch: Any, tmp_path: Path) -> None:
    _patch_fake_engine(monkeypatch)
    monkeypatch.setenv("REDTHREAD_DRY_RUN", "false")
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, ["run", "--report-dir", "custom-reports"])
        manifest_path = next(Path("custom-reports").glob("*/manifest.json"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert manifest["artifact_dir"].startswith("custom-reports/campaign-")
    assert "custom-reports" in result.output


def test_run_keeps_direct_report_exports(monkeypatch: Any, tmp_path: Path) -> None:
    _patch_fake_engine(monkeypatch)
    monkeypatch.setenv("REDTHREAD_DRY_RUN", "false")
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            main,
            ["run", "--report-md", "operator.md", "--report-json", "operator.json"],
        )
        assert Path("operator.md").exists()
        assert Path("operator.json").exists()
        assert next(Path("reports").glob("*/manifest.json"))

    assert result.exit_code == 0


def test_run_help_groups_advanced_and_hides_research_controls() -> None:
    result = CliRunner().invoke(main, ["run", "--help"])

    assert result.exit_code == 0
    assert "Advanced options" in result.output
    assert "Research help" in result.output
    assert "--show-research" in result.output
    assert "--trace-all" not in result.output
    assert "--benchmark-fixture" not in result.output
    assert "--persona-weighting-plan" not in result.output
    assert "--include-internal-sidecars" not in result.output


def test_run_show_research_lists_hidden_controls() -> None:
    result = CliRunner().invoke(main, ["run", "--show-research"])

    assert result.exit_code == 0
    assert "Research controls hidden from normal help" in result.output
    assert "--trace-all" in result.output
    assert "--benchmark-fixture" in result.output
    assert "--persona-weighting-plan" in result.output
    assert "--include-internal-sidecars" in result.output
