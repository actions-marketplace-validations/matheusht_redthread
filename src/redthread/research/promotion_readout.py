"""Operator-facing promotion proof readouts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

PROMOTION_LADDER = "candidate_defense → validated_candidate → promotable_defense → active_guardrail"


def promotion_outcome_line(validation_status: str, promoted_count: int, dry_run: bool) -> str:
    """Return the one-line operator outcome for a promotion attempt."""
    if dry_run:
        return "dry_run: no production memory write"
    if validation_status == "validated" and promoted_count > 0:
        return f"active_guardrail written: {promoted_count}"
    if validation_status == "validated":
        return "validated, but no active guardrail was written"
    return "blocked: no active guardrail was written"


def state_count_line(state_by_trace: Mapping[str, str]) -> str:
    """Summarize promotion states in stable operator text."""
    if not state_by_trace:
        return "none"
    counts: dict[str, int] = {}
    for state in state_by_trace.values():
        counts[state] = counts.get(state, 0) + 1
    return ", ".join(f"{state}={count}" for state, count in sorted(counts.items()))


def trace_state_lines(
    state_by_trace: Mapping[str, str],
    evidence_by_trace: Mapping[str, str],
    promoted_trace_ids: Sequence[str] | None = None,
) -> list[str]:
    """Render trace-level promotion state and evidence mode."""
    promoted = set(promoted_trace_ids or [])
    lines: list[str] = []
    for trace_id, state in sorted(state_by_trace.items()):
        active_suffix = " -> active_guardrail" if trace_id in promoted else ""
        evidence = evidence_by_trace.get(trace_id, "unknown")
        lines.append(f"    - {trace_id}: state={state}{active_suffix}; evidence={evidence}")
    return lines


__all__ = [
    "PROMOTION_LADDER",
    "promotion_outcome_line",
    "state_count_line",
    "trace_state_lines",
]
