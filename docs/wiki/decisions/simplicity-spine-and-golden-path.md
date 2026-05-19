---
title: Simplicity Spine and Golden Path
type: decision
status: accepted
summary: RedThread should simplify around one evidence spine, one golden CLI path, and strict evidence honesty instead of exposing internal research complexity to normal operators.
source_of_truth:
  - README.md
  - docs/product.md
  - docs/PHASE_REGISTRY.md
  - docs/AGENT_ARCHITECTURE.md
  - docs/DEFENSE_PIPELINE.md
  - docs/ANTI_HALLUCINATION_SOP.md
  - docs/wiki/decisions/hide-learning-complexity-from-operator.md
  - docs/wiki/systems/orchestration-and-engine-runtime.md
  - docs/wiki/systems/promotion-and-revalidation.md
  - src/redthread/cli/run.py
  - src/redthread/cli/run_help.py
  - src/redthread/cli/run_reports.py
  - src/redthread/reporting/evidence_labels.py
  - src/redthread/reporting/evidence_summary.py
  - src/redthread/orchestration/supervisor.py
  - src/redthread/orchestration/graphs/attack_graph.py
  - src/redthread/orchestration/graphs/defense_graph.py
  - src/redthread/evaluation/pipeline.py
  - src/redthread/config/settings.py
updated_by: pi
updated_at: 2026-05-18
---

# Simplicity Spine and Golden Path

## Decision

RedThread should simplify around one operator and architecture spine:

```text
attack → judge → defend → replay → promotion evidence
```

The normal product path should be one golden CLI flow:

```bash
redthread run --objective "test this agent" --system-prompt "..."
```

The operator should get one clear report that answers:

1. What failed?
2. Why does the JudgeAgent believe it failed?
3. What defense was proposed?
4. What replay evidence exists?
5. Is this promotable, weak, or blocked?
6. What should the operator do next?

As of the Phase 1 through Phase 8 simplicity implementation, this command writes a standard report by default and the report carries explicit evidence truth fields:

- normal path: `reports/<campaign_id>/`
- dry-run path: `reports/<campaign_id>/dry-run/`
- `--report-dir` remains an override, not a requirement
- manifests include `evidence_labels`, `evidence_mode_counts`, and `evidence_uncertainty`
- `validated_candidate` is the canonical defense-candidate state; legacy `defense_deployed` remains only as a compatibility alias

Advanced research controls can remain, but they should not define the default experience.

## Product framing

RedThread should feel less like a research lab and more like a courtroom for AI security evidence.

That means the report should lead with:

- claim
- evidence
- uncertainty
- defense candidate
- replay result
- promotion status

It should not lead with internal algorithm mechanics, sidecar names, hidden plans, or debug-only artifacts.

## Essential complexity to keep

Do not simplify away these capabilities:

- PAIR, TAP, Crescendo, and MCTS as attack families.
- JudgeAgent ownership of confirmed findings.
- Explicit evidence classes.
- Replay gates.
- Defense validation.
- Candidate-versus-active promotion boundaries.
- Prompt-safe benchmark and artifact handling.
- Runtime truth for sealed, live, fallback, and degraded paths.

These are core to RedThread's promise: find the exploit, judge it, draft the fix, and prove what changed.

## Accidental complexity to reduce

The current simplification targets are:

1. **Operator path sprawl** — Phase 1 made standard report persistence the default and grouped CLI help into normal, advanced, and hidden research controls. Future flags should stay out of the normal path unless they reduce operator work.
2. **Fat orchestration surface** — Phase 3 kept `supervisor.py` as a compatibility facade and moved state, routing, graph construction, stage nodes, and finalization into smaller modules.
3. **Algorithm dispatch duplication** — Phase 4 added an attack runner registry so PAIR, TAP, Crescendo, and MCTS stay available without brittle inline dispatch.
4. **Settings sprawl** — Phase 6 split settings by concern while preserving flat `REDTHREAD_` compatibility and adding minimal `default`, `research`, and `ci` profiles.
5. **Weak TAP test surface** — Phase 4 replaced the empty TAP test with dry-run smoke/safety coverage.
6. **Fallback evidence overread risk** — Phase 2 added canonical evidence labels, counts, uncertainty notes, and tests so fallback evidence cannot render as clean live proof.
7. **Candidate versus active defense wording** — Phase 5 and Phase 8 made `validated_candidate` canonical and reserved `active_guardrail` for explicitly promoted controls.

## Naval simplicity lens

Use the simplest-thing-that-could-work order:

1. Question the requirement.
2. Delete the part or process step if it is not essential.
3. Simplify the remaining path.
4. Optimize only after the path is simple.
5. Automate only after the right path is clear.

For RedThread, this means deleting user-facing complexity before adding more knobs.

## Consequences

### Positive

- Operators learn one workflow first.
- Reports become easier to trust.
- Architecture work has a clear target shape.
- Advanced algorithms stay available without dominating the product surface.
- Evidence honesty remains stronger than demo polish.

### Costs

- Some advanced flags may become hidden, deprecated, or moved to research docs.
- Some files need extraction before feature work continues.
- Existing docs may need consolidation around the spine.
- Exact code changes still need phased implementation approval.

## Alternatives considered

### Remove advanced attack algorithms

Rejected. PAIR, TAP, Crescendo, and MCTS are essential discovery paths. The issue is surface complexity, not algorithm existence.

### Expose every internal artifact to operators

Rejected. This makes RedThread feel like a manual toolkit and conflicts with the existing decision to hide learning complexity from the operator.

### Treat weak signals as findings

Rejected. Weak signals can guide exploration, but JudgeAgent and replay gates own confirmed evidence.

### Optimize before deleting complexity

Rejected. Faster sprawl is still sprawl.

## Uncertainty

The 2026-05-18 subagent consensus from `plan-ceo-review`, `office-hours`, `redthread-cto`, and `reviewer` is session evidence. It was not stored as a standalone repo artifact before this page. Treat it as planning input, not independent test proof.

The implemented simplification pass did not delete compatibility aliases such as `defense_deployed`; those aliases should be deprecated through docs/API migration before removal.

## Related pages

- [Hide Learning Complexity From The Operator](hide-learning-complexity-from-operator.md)
- [Orchestration and Engine Runtime](../systems/orchestration-and-engine-runtime.md)
- [Promotion and Revalidation](../systems/promotion-and-revalidation.md)
- [RedThread Simplicity Implementation Plan](../research/redthread-simplicity-implementation-plan.md)

## Sources

- [../../../README.md](../../../README.md)
- [../../product.md](../../product.md)
- [../../PHASE_REGISTRY.md](../../PHASE_REGISTRY.md)
- [../../AGENT_ARCHITECTURE.md](../../AGENT_ARCHITECTURE.md)
- [../../DEFENSE_PIPELINE.md](../../DEFENSE_PIPELINE.md)
- [../../ANTI_HALLUCINATION_SOP.md](../../ANTI_HALLUCINATION_SOP.md)
- [hide-learning-complexity-from-operator.md](hide-learning-complexity-from-operator.md)
- [../systems/orchestration-and-engine-runtime.md](../systems/orchestration-and-engine-runtime.md)
- [../systems/promotion-and-revalidation.md](../systems/promotion-and-revalidation.md)
- [../../../src/redthread/cli/run.py](../../../src/redthread/cli/run.py)
- [../../../src/redthread/cli/run_help.py](../../../src/redthread/cli/run_help.py)
- [../../../src/redthread/cli/run_reports.py](../../../src/redthread/cli/run_reports.py)
- [../../../src/redthread/orchestration/supervisor.py](../../../src/redthread/orchestration/supervisor.py)
- [../../../src/redthread/orchestration/graphs/attack_graph.py](../../../src/redthread/orchestration/graphs/attack_graph.py)
- [../../../src/redthread/evaluation/pipeline.py](../../../src/redthread/evaluation/pipeline.py)
- [../../../src/redthread/config/settings.py](../../../src/redthread/config/settings.py)
- [Naval: The Simplest Thing That Could Possibly Work](https://nav.al/simplest)
