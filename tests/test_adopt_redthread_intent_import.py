"""Tests for native adopt-redthread intent evidence import."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from redthread.cli import main
from redthread.reporting import (
    ExternalEvidenceSource,
    adopt_redthread_intent_evidence_from_payload,
    campaign_candidates_from_external_evidence,
)


def _package() -> dict[str, object]:
    return {
        "schema_version": "redthread.intent_evidence.v1",
        "source": {
            "tool": "adopt-redthread",
            "input_type": "sanitized_intent_review",
            "raw_artifacts_included": False,
        },
        "privacy": {
            "sanitized": True,
            "raw_har_included": False,
            "raw_urls_included": False,
            "headers_included": False,
            "cookies_included": False,
            "bodies_included": False,
            "secrets_included": False,
        },
        "intent": {
            "not_a_finding": True,
            "authority_boundary": "unknown_or_sanitized_boundary_area",
        },
        "evidence": [
            {
                "id": "ev_001_001",
                "source_observation_id": "obs_001",
                "summary": "sanitized boundary-relevant signal",
                "strength": "weak",
                "limitations": ["raw values are not included"],
            }
        ],
        "attack_plan": {
            "steps": [
                {
                    "id": "step_001",
                    "subject_id": "subject_001",
                    "action": "collect approved boundary context before RedThread evaluation",
                    "expected_signal": "approved context is available for JudgeAgent review",
                    "success_condition": "JudgeAgent can decide whether a RedThread run is warranted",
                    "requires_raw_payload": False,
                    "requires_live_execution": False,
                    "supporting_evidence_ids": ["ev_001_001"],
                }
            ]
        },
        "redthread_import": {
            "recommended_workflow_type": "attack_judge_defend_validate",
            "requires_human_review": True,
            "judge_agent_required": True,
            "eligible_for_regression": False,
        },
    }


def test_native_import_maps_intent_evidence_to_weak_external_bundle() -> None:
    bundle = adopt_redthread_intent_evidence_from_payload(_package())

    assert bundle.schema_version == "redthread.external_evidence_bundle.v1"
    assert bundle.source == ExternalEvidenceSource.ADOPT_REDTHREAD
    assert bundle.evidence_mode == "weak_imported_evidence"
    assert bundle.promotion_impact == "none"
    assert len(bundle.items) == 2
    assert all(item.is_confirmed_finding is False for item in bundle.items)
    assert all(item.requires_judge_confirmation is True for item in bundle.items)
    assert bundle.items[1].candidate_probe_seed is not None

    candidates = campaign_candidates_from_external_evidence(bundle)
    assert candidates.schema_version == "redthread.external_campaign_candidates.v1"
    assert candidates.evidence_mode == "weak_imported_evidence"
    assert candidates.creates_regression_case is False
    assert candidates.probe_seeds[0].source_id == "step_001"


def test_native_import_rejects_live_execution_step() -> None:
    package = _package()
    package["attack_plan"]["steps"][0]["requires_live_execution"] = True  # type: ignore[index]

    with pytest.raises(ValueError, match="cannot require live execution"):
        adopt_redthread_intent_evidence_from_payload(package)


def test_native_import_rejects_finding_claim_boundary() -> None:
    package = _package()
    package["intent"]["not_a_finding"] = False  # type: ignore[index]

    with pytest.raises(ValueError, match="must declare not_a_finding"):
        adopt_redthread_intent_evidence_from_payload(package)


def test_native_import_cli_then_plan_writes_candidate_campaign(tmp_path: Path) -> None:
    input_path = tmp_path / "redthread_intent_evidence.json"
    evidence_path = tmp_path / "external-evidence.json"
    candidates_path = tmp_path / "candidate-campaign.json"
    input_path.write_text(json.dumps(_package()), encoding="utf-8")

    runner = CliRunner()
    imported = runner.invoke(
        main,
        ["evidence", "import-adopt-redthread", "--input", str(input_path), "--output", str(evidence_path)],
    )
    planned = runner.invoke(
        main,
        ["evidence", "plan", "--input", str(evidence_path), "--output", str(candidates_path)],
    )

    assert imported.exit_code == 0
    assert planned.exit_code == 0
    assert "adopt-redthread weak evidence" in imported.output
    assert "No scores" in imported.output
    assert "JudgeAgent confirmation is still required" in imported.output
    campaign = json.loads(candidates_path.read_text(encoding="utf-8"))
    assert campaign["source"] == "adopt-redthread"
    assert campaign["evidence_mode"] == "weak_imported_evidence"
    assert len(campaign["probe_seeds"]) == 1
    assert campaign["creates_promotion_claim"] is False
