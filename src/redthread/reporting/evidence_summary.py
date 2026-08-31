"""Campaign evidence summary collection for operator reports."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from redthread.models import CampaignResult
from redthread.reporting.evidence_labels import evidence_summary


def campaign_evidence_summary(campaign: CampaignResult) -> dict[str, Any]:
    """Build canonical evidence labels, counts, and uncertainty notes."""
    return evidence_summary(_observed_evidence_modes(campaign), _fallback_reasons(campaign))


def _observed_evidence_modes(campaign: CampaignResult) -> list[str]:
    modes = [str(campaign.metadata.get("runtime_mode", ""))]
    for result in campaign.results:
        modes.append(str(result.trace.metadata.get("judge_runtime_status", "")))
        modes.append(str(result.trace.metadata.get("evidence_class", "")))
    for record in _metadata_records(campaign.metadata.get("defense_records", [])):
        modes.extend(_defense_evidence_modes(record))
    return [mode for mode in modes if mode]


def _defense_evidence_modes(record: dict[str, Any]) -> list[str]:
    modes = [str(record.get("guardrail_status", ""))]
    validation = record.get("validation")
    if isinstance(validation, Mapping):
        modes.append(str(validation.get("evidence_mode", "")))
    return [mode for mode in modes if mode]


def _fallback_reasons(campaign: CampaignResult) -> list[str]:
    reasons = []
    for result in campaign.results:
        error = result.trace.metadata.get("judge_error")
        if error:
            reasons.append(str(error))
    return reasons


def _metadata_records(value: Any) -> list[dict[str, Any]]:
    return [dict(item) for item in value] if isinstance(value, list) else []


__all__ = ["campaign_evidence_summary"]
