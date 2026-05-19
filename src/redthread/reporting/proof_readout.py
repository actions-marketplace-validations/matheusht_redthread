"""Operator proof UX helpers for RedThread Markdown reports."""

from __future__ import annotations

from typing import Any

from redthread.reporting.models import OperatorArtifactBundle


def proof_readout_lines(bundle: OperatorArtifactBundle) -> list[str]:
    """Return top-of-report proof readout sections."""
    return [
        *_executive_summary_lines(bundle),
        *_proof_path_lines(bundle),
        *_next_action_lines(bundle),
    ]


def _executive_summary_lines(bundle: OperatorArtifactBundle) -> list[str]:
    readout = bundle.stakeholder_readout
    security = bundle.security_card
    return [
        "## Executive Summary",
        f"- What happened: {readout.confirmed_findings} JudgeAgent-confirmed finding(s) "
        f"across {readout.total_runs} run(s).",
        f"- Attack success rate: {security.attack_success_rate:.1%}",
        f"- Average JudgeAgent score: {security.average_judge_score:.2f}",
        f"- Evidence mode: {readout.evidence_mode}",
        f"- Promotion state: {_promotion_state(bundle)}",
        "",
    ]


def _proof_path_lines(bundle: OperatorArtifactBundle) -> list[str]:
    lines = [
        "## Why Trust This Report",
        "- JudgeAgent verdicts own confirmed findings; detector hints are weak context only.",
        "- Evidence labels and counts below show whether proof is live, sealed, fallback, or candidate evidence.",
    ]
    if bundle.evidence_uncertainty:
        lines.append("- Uncertainty is explicit; do not treat warnings as clean live proof.")
    lines.extend(_stage_lines(bundle))
    return [*lines, ""]


def _next_action_lines(bundle: OperatorArtifactBundle) -> list[str]:
    if bundle.vulnerability_report.finding_count:
        first = [
            "Review each finding owner, mitigation, and replay evidence.",
            "Promote guardrails only after promotable replay evidence and explicit approval.",
        ]
    else:
        first = ["Review scope and evidence limits before treating this as coverage proof."]
    lines = ["## What To Do Next"]
    lines.extend(f"- {item}" for item in first)
    lines.extend(f"- {item}" for item in bundle.pr_checklist.items)
    return [*lines, ""]


def _stage_lines(bundle: OperatorArtifactBundle) -> list[str]:
    stages = _hero_stages(bundle)
    if not stages:
        return ["- Proof path: not reported."]
    labels = []
    for stage in stages:
        labels.append(
            f"{stage.get('name', 'unknown')}={stage.get('status', 'unknown')}"
            f"/{stage.get('evidence_label', 'unknown')}"
        )
    return ["- Proof path: " + " → ".join(labels)]


def _promotion_state(bundle: OperatorArtifactBundle) -> str:
    hero = bundle.hero_proof
    metrics = hero.get("metrics", {}) if isinstance(hero, dict) else {}
    ci = bundle.ci_regression if isinstance(bundle.ci_regression, dict) else {}
    validated = int(metrics.get("validated_candidates", ci.get("validated_candidate_count", 0)) or 0)
    regressions = int(bundle.regression_pack_summary.case_count)
    if validated and regressions:
        return "validated candidate with regression evidence; still requires explicit promotion"
    if validated:
        return "validated candidate; not an active guardrail"
    if bundle.vulnerability_report.finding_count:
        return "finding confirmed; defense candidate not validated in this report"
    return "no confirmed finding in this report"


def _hero_stages(bundle: OperatorArtifactBundle) -> list[dict[str, Any]]:
    hero = bundle.hero_proof
    if not isinstance(hero, dict):
        return []
    stages = hero.get("stages", [])
    return [dict(stage) for stage in stages if isinstance(stage, dict)]


__all__ = ["proof_readout_lines"]
