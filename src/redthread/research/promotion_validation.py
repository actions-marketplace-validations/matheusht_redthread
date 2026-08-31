"""Promotion validation replay helpers."""

from __future__ import annotations

from redthread.config.settings import RedThreadSettings
from redthread.core.defense_models import DeploymentRecord
from redthread.core.defense_status import defense_promotion_state
from redthread.research.models import PhaseThreeProposal
from redthread.research.promotion_evidence import (
    PromotionEvidenceSummary,
    promotion_failure_reason,
    summarize_promotion_records,
)
from redthread.research.promotion_models import PromotionManifest, PromotionValidationResult
from redthread.research.promotion_support import eligible_records
from redthread.research.workspace import ResearchWorkspace


def build_promotion_validation(
    settings: RedThreadSettings,
    workspace: ResearchWorkspace,
    proposal: PhaseThreeProposal,
    manifest: PromotionManifest,
) -> PromotionValidationResult:
    """Replay promotion gates and return the structured validation result."""
    control = next((item for item in proposal.cycle.lane_summaries if item.lane == "control"), None)
    control_gate_passed = bool(
        control
        and control.average_asr <= float(manifest.revalidation_policy["control_max_average_asr"])
        and control.average_score <= float(manifest.revalidation_policy["control_max_average_score"])
    )
    lane_names = {item.lane for item in proposal.cycle.lane_summaries if item.lane is not None}
    records = eligible_records(settings, workspace, proposal)
    evidence_summary = summarize_promotion_records(records)
    status, failure_reason = _validation_status(
        proposal=proposal,
        lane_names=lane_names,
        control_gate_passed=control_gate_passed,
        record_count=len(records),
        evidence_summary=evidence_summary,
        require_report=bool(manifest.revalidation_policy.get("require_defense_validation_report")),
    )
    return PromotionValidationResult(
        promotion_id=manifest.promotion_id,
        proposal_id=proposal.proposal_id,
        replayed_cycle=proposal.cycle,
        control_gate_passed=control_gate_passed,
        eligible_trace_ids=sorted(records),
        defense_report_coverage=evidence_summary.report_coverage,
        defense_utility_gate=evidence_summary.utility_gate,
        promotion_state_by_trace=_promotion_states(records, evidence_summary.utility_gate, status),
        promotion_evidence_mode_by_trace={
            trace_id: record.validation.evidence_mode for trace_id, record in sorted(records.items())
        },
        missing_report_trace_ids=evidence_summary.missing_report_trace_ids,
        weak_evidence_trace_ids=evidence_summary.weak_evidence_trace_ids,
        failed_validation_trace_ids=evidence_summary.failed_validation_trace_ids,
        validation_failures_by_trace=evidence_summary.validation_failures_by_trace,
        validation_status=status,
        failure_reason=failure_reason,
    )


def _validation_status(
    *,
    proposal: PhaseThreeProposal,
    lane_names: set[str],
    control_gate_passed: bool,
    record_count: int,
    evidence_summary: PromotionEvidenceSummary,
    require_report: bool,
) -> tuple[str, str | None]:
    if not proposal.accepted:
        return "failed", "proposal was not accepted in the research plane"
    if not {"offense", "regression", "control"}.issubset(lane_names):
        return "failed", "proposal artifact does not contain the full supervisor pack"
    if not control_gate_passed:
        return "failed", "control gate failed during promotion replay"
    if proposal.eligible_trace_ids and record_count != len(set(proposal.eligible_trace_ids)):
        return "failed", "promotion artifacts reference missing research deployment records"
    if (require_report and evidence_summary.missing_report_trace_ids) or evidence_summary.validation_failures_by_trace:
        return "failed", promotion_failure_reason(evidence_summary)
    return "validated", None


def _promotion_states(
    records: dict[str, DeploymentRecord],
    utility_gate: dict[str, list[str]],
    status: str,
) -> dict[str, str]:
    return {
        trace_id: defense_promotion_state(
            validation_passed=record.validation.passed,
            utility_failures=_promotion_failures_for_state(utility_gate.get(trace_id, []), status),
        )
        for trace_id, record in sorted(records.items())
    }


def _promotion_failures_for_state(failures: list[str], status: str) -> list[str]:
    if status == "validated":
        return failures
    return failures or ["promotion_validation_failed"]


__all__ = ["build_promotion_validation"]
