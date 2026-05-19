from __future__ import annotations

import json
from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch
from click.testing import CliRunner

from redthread.cli import main
from redthread.research.workspace import ResearchWorkspace
from tests.research_promotion_helpers import append_research_record, proposal_payload


def test_research_promote_cli_surfaces_active_guardrail_write(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    workspace = ResearchWorkspace(tmp_path)
    workspace.ensure_layout()
    append_research_record(workspace, "trace-live")
    payload = proposal_payload(workspace, eligible_trace_ids=["trace-live"])
    workspace.proposal_path("proposal-123").write_text(json.dumps(payload), encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(main, ["research", "promote"])

    assert result.exit_code == 0
    assert "Outcome:   active_guardrail written: 1" in result.output
    assert "States:    promotable_defense=1" in result.output
    assert "trace-live: state=promotable_defense -> active_guardrail" in result.output
    assert "evidence=live_replay" in result.output


def test_research_promote_cli_surfaces_weak_evidence(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    workspace = ResearchWorkspace(tmp_path)
    workspace.ensure_layout()
    append_research_record(
        workspace,
        "trace-weak",
        validation_mode="dry_run",
        evidence_mode="sealed_dry_run_replay",
    )
    payload = proposal_payload(workspace, eligible_trace_ids=["trace-weak"])
    workspace.proposal_path("proposal-123").write_text(json.dumps(payload), encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(main, ["research", "promote", "--dry-run"])

    assert result.exit_code == 0
    assert "Outcome:   dry_run: no production memory write" in result.output
    assert "Ladder:    candidate_defense → validated_candidate → promotable_defense" in result.output
    assert "active_guardrail" in result.output
    assert "States:    validated_candidate=1" in result.output
    assert "trace-weak: state=validated_candidate" in result.output
    assert "evidence=sealed_dry_run_replay" in result.output
    assert "Weak evidence: trace-weak" in result.output
    assert "Failure map:" in result.output
    assert "evidence_mode_not_promotable:sealed_dry_run_replay" in result.output


def test_research_promote_inspect_cli_surfaces_missing_and_failed_buckets(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    workspace = ResearchWorkspace(tmp_path)
    workspace.ensure_layout()
    append_research_record(workspace, "trace-missing", with_report=False)
    payload = proposal_payload(workspace, eligible_trace_ids=["trace-missing"])
    workspace.proposal_path("proposal-123").write_text(json.dumps(payload), encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    promote = CliRunner().invoke(main, ["research", "promote", "--dry-run"])
    assert promote.exit_code == 0

    inspect = CliRunner().invoke(main, ["research", "promote-inspect"])

    assert inspect.exit_code == 0
    assert "Outcome:   dry_run: no production memory write" in inspect.output
    assert "States:    validated_candidate=1" in inspect.output
    assert "trace-missing: state=validated_candidate" in inspect.output
    assert "evidence=live_replay" in inspect.output
    assert "Missing:   trace-missing" in inspect.output
    assert "Weak:      trace-missing" in inspect.output
    assert "Fail map:" in inspect.output
    assert "missing_validation_report" in inspect.output
    assert "validation report missing" in inspect.output


def test_research_promote_inspect_cli_bridges_to_replay_case_failure_detail(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    workspace = ResearchWorkspace(tmp_path)
    workspace.ensure_layout()
    append_research_record(workspace, "trace-benign-regression", benign_passed=False)
    payload = proposal_payload(workspace, eligible_trace_ids=["trace-benign-regression"])
    workspace.proposal_path("proposal-123").write_text(json.dumps(payload), encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    promote = CliRunner().invoke(main, ["research", "promote", "--dry-run"])
    assert promote.exit_code == 0

    inspect = CliRunner().invoke(main, ["research", "promote-inspect"])

    assert inspect.exit_code == 0
    assert "Trace states:" in inspect.output
    assert "trace-benign-regression" in inspect.output
    assert "state=candidate_defense" in inspect.output
    assert "evidence=live_replay" in inspect.output
    assert "Trace detail:" in inspect.output
    assert "trace-benign-regression: evidence=live_replay; passed=False;" in inspect.output
    assert "failed_cases=capital_france" in inspect.output
    assert "capital_france (benign) -> benign regression" in inspect.output
