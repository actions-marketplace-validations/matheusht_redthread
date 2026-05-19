"""Canonical operator evidence labels and uncertainty summaries."""

from __future__ import annotations

from collections import Counter
from typing import Any, Final

SEALED: Final = "sealed"
LIVE_JUDGE: Final = "live_judge"
FALLBACK: Final = "fallback"
IMPORTED_WEAK_EVIDENCE: Final = "imported_weak_evidence"
SEALED_RUNTIME_REVIEW: Final = "sealed_runtime_review"
NARROW_LIVE_INTERCEPTION_PROOF: Final = "narrow_live_interception_proof"
CANDIDATE_DEFENSE: Final = "candidate_defense"
VALIDATED_CANDIDATE: Final = "validated_candidate"
PROMOTABLE_DEFENSE: Final = "promotable_defense"
ACTIVE_GUARDRAIL: Final = "active_guardrail"
UNKNOWN: Final = "unknown"

CANONICAL_EVIDENCE_LABELS: Final[dict[str, str]] = {
    SEALED: "Sealed deterministic evidence",
    LIVE_JUDGE: "Live JudgeAgent evidence",
    FALLBACK: "Fallback evidence; weaker than live judge",
    IMPORTED_WEAK_EVIDENCE: "Imported weak evidence; not a finding",
    SEALED_RUNTIME_REVIEW: "Sealed runtime review evidence",
    NARROW_LIVE_INTERCEPTION_PROOF: "Narrow live interception proof",
    CANDIDATE_DEFENSE: "Candidate defense; not validated or active",
    VALIDATED_CANDIDATE: "Validated defense candidate; not active guardrail",
    PROMOTABLE_DEFENSE: "Promotable defense evidence; awaits operator approval",
    ACTIVE_GUARDRAIL: "Active guardrail; eligible for runtime injection",
}

_MODE_ALIASES: Final[dict[str, str]] = {
    "sealed_dry_run": SEALED,
    "sealed_heuristic": SEALED,
    "sealed_dry_run_replay": SEALED,
    "sealed_replay": SEALED,
    "sealed_local_replay": SEALED,
    "sealed_passthrough": SEALED,
    "live": LIVE_JUDGE,
    "live_judge": LIVE_JUDGE,
    "live_replay": LIVE_JUDGE,
    "live_re_evaluated": LIVE_JUDGE,
    "live_judge_fallback": FALLBACK,
    "live_validation_error": FALLBACK,
    "live_judge_error_passthrough": FALLBACK,
    "live_empty_trace_passthrough": FALLBACK,
    "weak_imported_evidence": IMPORTED_WEAK_EVIDENCE,
    "imported_weak_evidence": IMPORTED_WEAK_EVIDENCE,
    "sealed_runtime_review": SEALED_RUNTIME_REVIEW,
    "live_interception": NARROW_LIVE_INTERCEPTION_PROOF,
    "narrow_live_interception_proof": NARROW_LIVE_INTERCEPTION_PROOF,
    "candidate_defense": CANDIDATE_DEFENSE,
    "candidate_guardrail": CANDIDATE_DEFENSE,
    "validated_candidate": VALIDATED_CANDIDATE,
    "defense_candidate": VALIDATED_CANDIDATE,
    "promotable_evidence": PROMOTABLE_DEFENSE,
    "promotable_defense": PROMOTABLE_DEFENSE,
    "active_guardrail": ACTIVE_GUARDRAIL,
}

_DEGRADED_LABELS: Final = {FALLBACK, IMPORTED_WEAK_EVIDENCE, UNKNOWN}


def normalize_evidence_label(mode: str | None) -> str:
    """Map a raw mode/class string to a canonical operator label key."""
    if not mode:
        return UNKNOWN
    value = mode.lower().strip()
    if value in CANONICAL_EVIDENCE_LABELS:
        return value
    return _MODE_ALIASES.get(value, UNKNOWN)


def evidence_label_summary(modes: list[str]) -> dict[str, str]:
    """Return canonical label descriptions for observed modes."""
    labels = {normalize_evidence_label(mode) for mode in modes}
    labels.discard(UNKNOWN)
    return {label: CANONICAL_EVIDENCE_LABELS[label] for label in sorted(labels)}


def evidence_mode_counts(modes: list[str]) -> dict[str, int]:
    """Count observed modes by canonical operator label."""
    labels = [normalize_evidence_label(mode) for mode in modes]
    counts = Counter(label for label in labels if label != UNKNOWN)
    return dict(sorted(counts.items()))


def evidence_uncertainty_notes(modes: list[str], fallback_reasons: list[str] | None = None) -> list[str]:
    """Return operator-facing uncertainty notes for evidence mixes."""
    counts = evidence_mode_counts(modes)
    notes: list[str] = []
    if len(counts) > 1:
        notes.append("Mixed evidence modes are present; read counts before comparing scores.")
    if FALLBACK in counts:
        reason_text = _reason_text(fallback_reasons or [])
        notes.append(f"Fallback evidence is degraded and weaker than live JudgeAgent proof{reason_text}.")
    if IMPORTED_WEAK_EVIDENCE in counts:
        notes.append("Weak imported evidence is planning context only; it cannot create findings or severity.")
    if SEALED in counts and LIVE_JUDGE not in counts:
        notes.append("Sealed evidence is deterministic/offline proof, not live provider confirmation.")
    if VALIDATED_CANDIDATE in counts and ACTIVE_GUARDRAIL not in counts:
        notes.append("Validated defense candidates are not active runtime guardrails until promoted.")
    if any(label in _DEGRADED_LABELS for label in counts):
        notes.append("Do not present degraded evidence as clean live proof.")
    return notes


def evidence_summary(modes: list[str], fallback_reasons: list[str] | None = None) -> dict[str, Any]:
    """Build a stable report-ready evidence summary."""
    return {
        "labels": evidence_label_summary(modes),
        "counts": evidence_mode_counts(modes),
        "uncertainty_notes": evidence_uncertainty_notes(modes, fallback_reasons),
    }


def _reason_text(reasons: list[str]) -> str:
    clean = sorted({reason for reason in reasons if reason})
    return f"; reason(s): {', '.join(clean)}" if clean else ""


__all__ = [
    "ACTIVE_GUARDRAIL",
    "CANONICAL_EVIDENCE_LABELS",
    "CANDIDATE_DEFENSE",
    "FALLBACK",
    "IMPORTED_WEAK_EVIDENCE",
    "LIVE_JUDGE",
    "NARROW_LIVE_INTERCEPTION_PROOF",
    "PROMOTABLE_DEFENSE",
    "SEALED",
    "SEALED_RUNTIME_REVIEW",
    "UNKNOWN",
    "VALIDATED_CANDIDATE",
    "evidence_label_summary",
    "evidence_mode_counts",
    "evidence_summary",
    "evidence_uncertainty_notes",
    "normalize_evidence_label",
]
