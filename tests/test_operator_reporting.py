"""Tests for Slice 6 guide-style operator artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from redthread.config.settings import RedThreadSettings
from redthread.engine_transcript import write_transcript
from redthread.models import CampaignConfig, CampaignResult
from redthread.orchestration.campaign_planning import build_campaign_plan
from redthread.reporting import (
    build_operator_artifact_bundle,
    operator_artifacts_to_json,
    operator_artifacts_to_markdown,
    write_campaign_report_artifacts,
)
from tests.operator_reporting_helpers import make_campaign, make_result


def test_operator_artifact_bundle_includes_scope_risks_strategies_and_verdicts() -> None:
    campaign = make_campaign()
    plan = build_campaign_plan(
        {
            "objective": campaign.config.objective,
            "target_system_prompt": campaign.config.target_system_prompt,
            "risks": ["sensitive_data_exfiltration"],
            "strategies": {"include": ["static_seed_replay"]},
            "scope": {"target_ids": ["support-agent-dev"], "allowed_tools": ["target_llm"]},
        }
    )

    bundle = build_operator_artifact_bundle(campaign, plan=plan)

    assert bundle.schema_version == "redthread.operator_artifacts.v1"
    assert bundle.rules_of_engagement.scope.target_ids == ["support-agent-dev"]
    assert bundle.rules_of_engagement.risks_tested == ["sensitive_data_exfiltration"]
    assert bundle.rules_of_engagement.strategies_used == ["static_seed_replay"]
    assert bundle.vulnerability_report.finding_count == 1
    assert len(bundle.vulnerability_report.judge_verdicts) == 2
    assert bundle.security_card.attack_success_rate == 0.5
    assert bundle.evidence_labels["sealed"] == "Sealed deterministic evidence"
    assert bundle.evidence_mode_counts["sealed"] == 1
    assert any("Sealed evidence" in note for note in bundle.evidence_uncertainty)


def test_fallback_evidence_is_not_rendered_as_clean_live_proof() -> None:
    fallback = make_result(jailbreak=True, score=4.8)
    fallback.trace.metadata["judge_runtime_status"] = "live_judge_error_passthrough"
    fallback.trace.metadata["judge_error"] = "ProviderTimeout"
    campaign = CampaignResult(
        config=CampaignConfig(
            objective="fallback report test",
            target_system_prompt="You are a support assistant.",
            rubric_name="sensitive_info",
            num_personas=1,
        ),
        results=[fallback],
        metadata={"runtime_mode": "live"},
    )

    bundle = build_operator_artifact_bundle(campaign)
    markdown = operator_artifacts_to_markdown(bundle)

    assert bundle.evidence_mode_counts["fallback"] == 1
    assert "fallback: 1 (Fallback evidence; weaker than live judge)" in markdown
    assert "reason(s): ProviderTimeout" in markdown
    assert "Do not present degraded evidence as clean live proof" in markdown
    assert bundle.hero_proof["stages"][1]["evidence_label"] == "fallback"


def test_regression_links_are_included_in_report_artifacts() -> None:
    campaign = make_campaign()
    finding = campaign.results[0]

    bundle = build_operator_artifact_bundle(
        campaign,
        regression_links=[
            {
                "source_finding_id": finding.id,
                "source_trace_id": finding.trace.id,
                "regression_case_id": "regression-abc123",
                "status": "regression_case_created",
            }
        ],
    )

    report_finding = bundle.vulnerability_report.findings[0]
    assert report_finding.regression_case_id == "regression-abc123"
    assert report_finding.regression_status == "regression_case_created"
    assert bundle.regression_pack_summary.case_count == 1


def test_markdown_export_contains_required_operator_sections_and_no_overclaim() -> None:
    markdown = operator_artifacts_to_markdown(build_operator_artifact_bundle(make_campaign()))

    assert "## Executive Summary" in markdown
    assert "What happened: 1 JudgeAgent-confirmed finding(s) across 2 run(s)." in markdown
    assert "## Why Trust This Report" in markdown
    assert "JudgeAgent verdicts own confirmed findings" in markdown
    assert "Proof path: attack=" in markdown
    assert "## What To Do Next" in markdown
    assert "finding confirmed; defense candidate not validated in this report" in markdown
    assert "## Rules of Engagement Summary" in markdown
    assert "## Evidence & Uncertainty" in markdown
    assert "sealed: 1 (Sealed deterministic evidence)" in markdown
    assert "Sealed evidence is deterministic/offline proof" in markdown
    assert "## Vulnerability Report" in markdown
    assert "## Model/System Security Card" in markdown
    assert "## PR Checklist" in markdown
    assert "## Stakeholder Readout" in markdown
    assert "## Regression Pack Summary" in markdown
    assert "Detector hints: weak signal context only" in markdown
    assert "JudgeAgent verdict" in markdown
    assert "Detector hints: proof" not in markdown


def test_json_export_has_stable_shape() -> None:
    data = json.loads(operator_artifacts_to_json(build_operator_artifact_bundle(make_campaign())))

    assert data["schema_version"] == "redthread.operator_artifacts.v1"
    assert data["vulnerability_report"]["finding_count"] == 1
    assert data["vulnerability_report"]["findings"][0]["judge_verdict"] == "confirmed_jailbreak"
    assert data["regression_pack_summary"]["links"] == []


def test_campaign_report_artifacts_persist_standard_manifest(tmp_path: Path) -> None:
    bundle = build_operator_artifact_bundle(make_campaign())

    manifest = write_campaign_report_artifacts(bundle, tmp_path / "reports")
    manifest_path = Path(manifest.artifact_dir) / "manifest.json"
    hero_path = Path(manifest.hero_proof)
    ci_path = Path(manifest.ci_regression)

    assert manifest.schema_version == "redthread.operator_report_manifest.v1"
    assert Path(manifest.markdown_report).exists()
    assert Path(manifest.json_report).exists()
    assert hero_path.exists()
    assert ci_path.exists()
    assert manifest_path.exists()
    manifest_data = json.loads(manifest_path.read_text())
    assert json.loads(hero_path.read_text())["stages"][-1]["name"] == "ci_regression"
    assert manifest_data["evidence_labels"]["sealed"] == "Sealed deterministic evidence"
    assert manifest_data["evidence_mode_counts"]["sealed"] == 1
    assert "Sealed evidence is deterministic/offline proof" in manifest_data["evidence_uncertainty"][0]
    assert "redthread test golden" in ci_path.read_text()
    assert "weak evidence" in " ".join(manifest.bridge_prep_notes)


def test_hero_proof_bundle_tracks_attack_judge_and_regression_stages() -> None:
    bundle = build_operator_artifact_bundle(make_campaign())

    proof = bundle.hero_proof

    assert proof["schema_version"] == "redthread.hero_proof.v1"
    assert [stage["name"] for stage in proof["stages"]] == [
        "attack",
        "judge",
        "defense_candidate",
        "replay",
        "benign_check",
        "ci_regression",
    ]
    assert proof["metrics"]["confirmed_findings"] == 1
    assert proof["ci_regression"]["recommended_command"] == "redthread test golden"


def test_transcript_summary_links_operator_report_manifest(tmp_path: Path) -> None:
    campaign = make_campaign()
    bundle = build_operator_artifact_bundle(campaign)
    manifest = write_campaign_report_artifacts(bundle, tmp_path / "reports")
    campaign.metadata["operator_report_manifest"] = manifest.model_dump(mode="json")
    settings = RedThreadSettings(log_dir=tmp_path / "logs", memory_dir=tmp_path / "memory")
    settings.log_dir.mkdir(parents=True, exist_ok=True)

    write_transcript(settings, campaign)
    first_line = (settings.log_dir / f"{campaign.id}.jsonl").read_text(encoding="utf-8").splitlines()[0]
    summary = json.loads(first_line)

    assert summary["operator_report_manifest"]["schema_version"] == "redthread.operator_report_manifest.v1"
    assert summary["operator_report_manifest"]["campaign_id"] == campaign.id
