"""Promotion-specific research models."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from redthread.research.models import SupervisorCycleSummary


class PromotionRecord(BaseModel):
    """Audit record for explicit research-to-production promotion steps."""

    promotion_id: str
    proposal_id: str
    manifest_ref: str
    validation_ref: str
    promoted_deployments: int
    promoted_trace_ids: list[str] = Field(default_factory=list)
    source_memory_dir: str
    target_memory_dir: str
    proposal_fingerprint: str
    validation_status: str = "pending"
    defense_report_refs: list[str] = Field(default_factory=list)
    dry_run: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PromotionManifest(BaseModel):
    """Frozen inputs for one research-to-production promotion attempt."""

    promotion_id: str
    proposal_id: str
    session_tag: str
    source_patch_artifact: str
    baseline_registry_ref: str | None = None
    checkpoint_refs: list[str] = Field(default_factory=list)
    mutation_refs: list[str] = Field(default_factory=list)
    expected_targets: list[str] = Field(default_factory=list)
    defense_report_refs: list[str] = Field(default_factory=list)
    research_memory_snapshot_ref: str | None = None
    revalidation_policy: dict[str, float | bool | str] = Field(default_factory=dict)


class PromotionValidationResult(BaseModel):
    """Result of replaying the proposal acceptance contract during promotion."""

    promotion_id: str
    proposal_id: str
    replayed_cycle: SupervisorCycleSummary
    control_gate_passed: bool
    eligible_trace_ids: list[str] = Field(default_factory=list)
    defense_report_coverage: dict[str, str] = Field(default_factory=dict)
    defense_utility_gate: dict[str, list[str]] = Field(default_factory=dict)
    promotion_state_by_trace: dict[str, str] = Field(default_factory=dict)
    promotion_evidence_mode_by_trace: dict[str, str] = Field(default_factory=dict)
    missing_report_trace_ids: list[str] = Field(default_factory=list)
    weak_evidence_trace_ids: list[str] = Field(default_factory=list)
    failed_validation_trace_ids: list[str] = Field(default_factory=list)
    validation_failures_by_trace: dict[str, list[str]] = Field(default_factory=dict)
    validation_status: str
    failure_reason: str | None = None


class PromotionCheckpoint(BaseModel):
    """Step-aware checkpoint for resumable promotion runs."""

    checkpoint_id: str
    promotion_id: str
    proposal_id: str
    step: str
    manifest_ref: str | None = None
    validation_ref: str | None = None
    result_ref: str | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


__all__ = [
    "PromotionCheckpoint",
    "PromotionManifest",
    "PromotionRecord",
    "PromotionValidationResult",
]
