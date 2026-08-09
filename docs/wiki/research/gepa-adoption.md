---
title: GEPA Adoption Lane
type: research
status: active
summary: Current synthesis of the hidden, fully contained GEPA reflective prompt-optimizer adoption lane and its safety contracts.
source_of_truth:
  - docs/PHASE_REGISTRY.md
  - docs/current_repo_state.md
  - src/redthread/research/gepa_allowlist.py
  - src/redthread/research/gepa_side_info.py
  - src/redthread/research/gepa_score.py
updated_by: opencode
updated_at: 2026-08-09
---

# GEPA Adoption Lane

## Research question

Can a reflective prompt optimizer (GEPA, arXiv 2507.19457) improve RedThread's
attacker prompt profiles without ever touching the judge, rubrics, promotion logic,
defense assets, or source files, and without collapsing the authority ladder between
optimizer-accept and RedThread promotion?

## Current synthesis

GEPA is adopted as a hidden, additive research lane. It is not part of the default
operator path and surfaces only behind hidden `redthread research gepa-*` commands.
`gepa==0.1.1` and `litellm>=1.0` are optional (`[research-gepa]` extra) and imported
lazily.

Progress:

- **Phase 0 — shadow harness** (merged): dependency-free lifecycle proving
  containment before a real optimizer exists.
- **Phase 1 — prompt-profile adapter** (adapter merged, live spike file present):
  `RedThreadGEPAAdapter` wraps research evaluation; the throwaway lift-spike script
  answers whether reflective + Pareto-selected prompt optimization beats the hard-coded
  mutation table on a held-out objective.
- **Phase 2 — Pareto frontier** (merged): replaces max-composite winner-collapse with a
  true Pareto frontier over per-objective score vectors; specialists survive.
- **Phase 3 — defense-lane spike** (working tree, uncommitted): GEPA over defense
  architect prompt templates.
- **Phase 4 — source-lane spike** (working tree, uncommitted): GEPA selects bounded
  Phase 5 source mutations without applying them.

## Safety contracts

1. **Allowlist** — only `pair.system_suffix`, `tap.system_suffix`, `tap.strategies`,
   `crescendo.system_suffix`, `mcts.system_suffix` are optimizable. Unknown keys fail
   before application.
2. **Redaction** — `gepa_side_info` is the only channel to a reflection LM; it is
   transcript-free, scrubs canaries/secrets/emails, and `assert_clean` fails closed.
3. **Control gate** — control lane is a fail-closed gate, never a reward bonus.
4. **Authority ladder** — `accepted_by_gepa`, `accepted_by_redthread_supervisor`, and
   promotion status stay separate; optimizer acceptance never writes production state.
5. **Budget** — live optimization requires explicit `reflection_lm` + positive
   `max_metric_calls`.
6. **Runtime confinement** — snapshots stay under `autoresearch/runtime/gepa/`.

## Evidence

- Phase 0 tests: allowlist, snapshot confinement, redaction, control-fail rejection,
  split overlap, budget stop, no promotion/memory writes.
- Phase 1 adapter tests: score/output alignment, objective breakdown, allowlist
  rejection, redacted reflective dataset, budget guard.
- Phase 2 tests: domination, specialist preservation, dominated exclusion, leader
  weighting, seeded-selection determinism, control-axis exclusion.
- Phase 3/4 tests exist in the working tree but are not yet committed.

## Contradictions / uncertainty

- The exact reward normalization (`ASR_WEIGHT=0.6`, `JUDGE_WEIGHT=0.4`) is provisional
  and flagged as an open Phase 1+ decision.
- Whether reflective prompt optimization actually lifts held-out objectives is an
  open empirical question; the live spike is the proof vehicle but has not been run
  against a live target yet.
- Phase 3/4 live integration is not committed and its promotion path is not final.

## Next questions

- Does the live lift-spike show a GO or NO-GO on the held-out objective?
- Does the defense-lane (Phase 3) preserve benign-utility while blocking exploits?
- Does the source-lane (Phase 4) stay within the bounded Phase 5 mutation surface?
