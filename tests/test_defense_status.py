from __future__ import annotations

from redthread.core.defense_status import (
    ACTIVE_GUARDRAIL,
    CANDIDATE_DEFENSE,
    PROMOTABLE_DEFENSE,
    VALIDATED_CANDIDATE,
    active_guardrail_metadata,
    candidate_flags,
    defense_promotion_state,
    inactive_candidate_metadata,
    validated_candidate,
    validated_candidate_count,
    validated_candidate_count_fields,
)


def test_candidate_flags_include_legacy_alias() -> None:
    flags = candidate_flags(True)

    assert flags["validated_candidate"] is True
    assert flags["defense_deployed"] is True


def test_validated_candidate_prefers_canonical_key() -> None:
    assert validated_candidate({"validated_candidate": False, "defense_deployed": True}) is False
    assert validated_candidate({"defense_deployed": True}) is True


def test_validated_candidate_count_prefers_canonical_key() -> None:
    count = validated_candidate_count({"defense_validated_candidates": 2, "defense_deployments": 9})

    assert count == 2
    assert validated_candidate_count_fields(count) == {
        "defense_validated_candidates": 2,
        "defense_deployments": 2,
    }


def test_inactive_candidate_metadata_never_marks_candidate_active() -> None:
    metadata = inactive_candidate_metadata(True)

    assert metadata["validated_candidate"] is True
    assert metadata["active_guardrail"] is False
    assert metadata["deployed"] is False
    assert metadata["promotion_status"] == "not_promoted"


def test_active_guardrail_metadata_marks_explicit_promotion() -> None:
    metadata = active_guardrail_metadata()

    assert metadata["validated_candidate"] is True
    assert metadata["active_guardrail"] is True
    assert metadata["deployed"] is True
    assert metadata["promotion_status"] == ACTIVE_GUARDRAIL


def test_defense_promotion_state_chain() -> None:
    assert defense_promotion_state(validation_passed=False, utility_failures=[]) == CANDIDATE_DEFENSE
    assert defense_promotion_state(validation_passed=True, utility_failures=["weak"]) == VALIDATED_CANDIDATE
    assert defense_promotion_state(validation_passed=True, utility_failures=[]) == PROMOTABLE_DEFENSE
    assert defense_promotion_state(validation_passed=True, utility_failures=[], active=True) == ACTIVE_GUARDRAIL
