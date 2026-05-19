---
title: Promotion and Revalidation
type: system
status: active
summary: How RedThread keeps proposal acceptance, validation evidence, and promotion discipline separate from mutation execution.
source_of_truth:
  - docs/AUTORESEARCH_PHASE5.md
  - docs/AUTORESEARCH_PHASE6.md
  - docs/DEFENSE_PIPELINE.md
  - docs/PHASE_REGISTRY.md
  - src/redthread/core/guardrail_loader.py
  - src/redthread/memory/index.py
updated_by: pi
updated_at: 2026-05-18
---

# Promotion and Revalidation

## Scope

This page summarizes the safety discipline around moving from candidate mutation or defense proposal to something eligible for promotion.

## Core idea

RedThread separates:
- mutation generation
- validation
- operator/supervisor acceptance
- promotion

That separation is one of the main safety boundaries in the system.

## Main controls

### Explicit accept/reject boundary
Autoresearch candidates do not become production-worthy just because they were generated.

The documented workflow preserves a formal supervisor decision boundary before promotion eligibility.

### Reverse patch artifacts
Patch reversibility is part of the contract, not an optional convenience.

That makes rejection safe and inspectable.

### Protected surfaces
Promotion logic itself is protected from the mutation lanes.

This is critical because otherwise the system could evolve the gatekeeper instead of only evolving the candidate.

### Defense validation evidence
The defense pipeline includes sealed replay and structured validation reporting. Promotion later depends on evidence, not just a proposed clause.

Promotion should treat defense evidence classes conservatively:
- `candidate_defense` is generated but not validated
- `validated_candidate` passed replay/indexing checks but is not active
- `promotable_defense` has evidence suitable for operator approval
- `active_guardrail` is promoted and eligible for runtime injection
- `live_replay` is the only promotable defense validation evidence class
- `sealed_dry_run_replay` is useful sealed evidence, but not strong enough for promotion
- `live_validation_error` means live replay evidence is incomplete, so promotion must fail closed

As of Phase 11, promotion validation persists:
- `promotion_state_by_trace`
- `promotion_evidence_mode_by_trace`
- `defense_utility_gate`
- weak evidence trace IDs
- failed validation trace IDs

This lets operators see why a trace stopped at `validated_candidate` instead of becoming `promotable_defense` or `active_guardrail`.

As of Phase 12, `redthread research promote` and `redthread research promote-inspect` render this evidence directly for operators. The readout includes the defense ladder, outcome line, state counts, trace-level state, trace-level evidence mode, and failure buckets. A successful explicit promotion shows `active_guardrail written: N`; dry-run and failed promotion clearly say no production memory write occurred.

As of Phase 13, runtime injection has a separate audit proof. `GuardrailLoader` writes `logs/guardrail_audit.jsonl` with the injection action, active guardrail count, active trace IDs, clause hashes, target model, prompt hash, and source. This proves what was injected or skipped without requiring raw guardrail clause text in the audit event. Structured deployment records remain authoritative; legacy markdown is only a compatibility fallback.

`defense_deployed` is deprecated wording. In current artifacts it remains only as a backward-compatible alias for `validated_candidate`, not proof of active production deployment.

Promotion validation now also persists operator-facing buckets:
- `missing_report_trace_ids`
- `weak_evidence_trace_ids`
- `failed_validation_trace_ids`
- `validation_failures_by_trace`

This matters because promotion is not magic approval.
It is a replayed evidence check with explicit reasons for why a trace was blocked.
Operators should be able to see whether the problem was:
- missing validation evidence
- weak or non-promotable evidence
- failed exploit-blocking or benign-utility replay

## Why it matters

Without this discipline, "self-improvement" would quickly become unsafe self-modification.

The project's current phase explicitly rejects that model.

## Relationship to bounded autoresearch

Promotion discipline is what turns bounded mutation into a safe research workflow instead of uncontrolled recursive editing.

## Related pages

- [../research/bounded-autoresearch.md](../research/bounded-autoresearch.md)
- [../../AUTORESEARCH_PHASE5.md](../../AUTORESEARCH_PHASE5.md)
- [../../AUTORESEARCH_PHASE6.md](../../AUTORESEARCH_PHASE6.md)
- [../../DEFENSE_PIPELINE.md](../../DEFENSE_PIPELINE.md)
