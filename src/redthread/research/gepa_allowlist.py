"""Allowlist for GEPA-optimizable prompt-profile components.

Phase 0 keeps the GEPA search space tiny and explicit. A candidate may only touch
the attacker prompt-profile fields named here. Anything else — judge, rubrics,
golden datasets, promotion logic, defense assets, source files — is unreachable by
construction: unknown keys are rejected before a candidate is ever applied.

The allowed keys are dotted ``section.field`` references into the prompt-profile
structure produced by ``research.prompt_profiles.default_prompt_profiles``.
"""

from __future__ import annotations

from collections.abc import Mapping

ALLOWED_COMPONENT_FIELDS: frozenset[str] = frozenset(
    {
        "pair.system_suffix",
        "tap.system_suffix",
        "tap.strategies",
        "crescendo.system_suffix",
        "mcts.system_suffix",
    }
)


class AllowlistViolation(ValueError):
    """Raised when a GEPA candidate references a field outside the allowlist."""


def unknown_fields(candidate: Mapping[str, object]) -> set[str]:
    """Return the candidate keys that are not on the allowlist."""
    return set(candidate) - ALLOWED_COMPONENT_FIELDS


def is_allowlisted(candidate: Mapping[str, object]) -> bool:
    """Return True only if every candidate field is allowlisted."""
    return not unknown_fields(candidate)


def assert_allowlisted(candidate: Mapping[str, object]) -> None:
    """Raise ``AllowlistViolation`` if the candidate touches a non-allowlisted field."""
    unknown = unknown_fields(candidate)
    if unknown:
        allowed = ", ".join(sorted(ALLOWED_COMPONENT_FIELDS))
        raise AllowlistViolation(
            f"GEPA candidate references non-allowlisted field(s): {sorted(unknown)}. "
            f"Allowed fields: {allowed}."
        )
