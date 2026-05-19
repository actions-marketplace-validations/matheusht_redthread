"""Canonical defense status keys and compatibility aliases."""

from __future__ import annotations

from typing import Any, Final

CANDIDATE_DEFENSE: Final = "candidate_defense"
VALIDATED_CANDIDATE: Final = "validated_candidate"
PROMOTABLE_DEFENSE: Final = "promotable_defense"
DEFENSE_DEPLOYED_ALIAS: Final = "defense_deployed"
DEFENSE_VALIDATED_CANDIDATES: Final = "defense_validated_candidates"
DEFENSE_DEPLOYMENTS_ALIAS: Final = "defense_deployments"
ACTIVE_GUARDRAIL: Final = "active_guardrail"
DEPLOYED_ALIAS: Final = "deployed"
PROMOTION_STATUS: Final = "promotion_status"


def candidate_flags(validated: bool) -> dict[str, bool]:
    """Return canonical candidate truth plus deprecated record alias."""
    return {
        VALIDATED_CANDIDATE: validated,
        DEFENSE_DEPLOYED_ALIAS: validated,
    }


def validated_candidate(record: dict[str, Any]) -> bool:
    """Read canonical validated-candidate truth with legacy fallback."""
    return bool(record.get(VALIDATED_CANDIDATE, record.get(DEFENSE_DEPLOYED_ALIAS)))


def validated_candidate_count(state: dict[str, Any]) -> int:
    """Read canonical supervisor count with legacy fallback."""
    return int(state.get(DEFENSE_VALIDATED_CANDIDATES, state.get(DEFENSE_DEPLOYMENTS_ALIAS, 0)))


def validated_candidate_count_fields(count: int) -> dict[str, int]:
    """Return canonical supervisor count plus deprecated alias."""
    return {
        DEFENSE_VALIDATED_CANDIDATES: count,
        DEFENSE_DEPLOYMENTS_ALIAS: count,
    }


def inactive_candidate_metadata(validated: bool) -> dict[str, bool | str]:
    """Return candidate metadata that must not imply active deployment."""
    return {
        DEPLOYED_ALIAS: False,
        ACTIVE_GUARDRAIL: False,
        VALIDATED_CANDIDATE: validated,
        PROMOTION_STATUS: "not_promoted",
    }


def active_guardrail_metadata() -> dict[str, bool | str]:
    """Return explicit metadata for a promoted active guardrail."""
    return {
        DEPLOYED_ALIAS: True,
        ACTIVE_GUARDRAIL: True,
        VALIDATED_CANDIDATE: True,
        PROMOTION_STATUS: ACTIVE_GUARDRAIL,
    }


def defense_promotion_state(
    *,
    validation_passed: bool,
    utility_failures: list[str],
    active: bool = False,
) -> str:
    """Map validation/promotion evidence into the canonical defense state chain."""
    if active:
        return ACTIVE_GUARDRAIL
    if not validation_passed:
        return CANDIDATE_DEFENSE
    if utility_failures:
        return VALIDATED_CANDIDATE
    return PROMOTABLE_DEFENSE


__all__ = [
    "ACTIVE_GUARDRAIL",
    "CANDIDATE_DEFENSE",
    "DEFENSE_DEPLOYED_ALIAS",
    "DEFENSE_DEPLOYMENTS_ALIAS",
    "DEFENSE_VALIDATED_CANDIDATES",
    "DEPLOYED_ALIAS",
    "PROMOTABLE_DEFENSE",
    "PROMOTION_STATUS",
    "VALIDATED_CANDIDATE",
    "active_guardrail_metadata",
    "candidate_flags",
    "defense_promotion_state",
    "inactive_candidate_metadata",
    "validated_candidate",
    "validated_candidate_count",
    "validated_candidate_count_fields",
]
