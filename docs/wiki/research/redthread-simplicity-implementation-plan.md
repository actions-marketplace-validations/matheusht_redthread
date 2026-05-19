---
title: RedThread Simplicity Implementation Plan
type: research
status: active
summary: Exact phased plan for turning the simplicity-spine decision into product, architecture, orchestration, evaluation, defense, memory/wiki, and reporting changes without weakening evidence integrity.
source_of_truth:
  - README.md
  - docs/product.md
  - docs/TECH_STACK.md
  - docs/PHASE_REGISTRY.md
  - docs/AGENT_ARCHITECTURE.md
  - docs/DEFENSE_PIPELINE.md
  - docs/ANTI_HALLUCINATION_SOP.md
  - docs/wiki/decisions/simplicity-spine-and-golden-path.md
  - docs/wiki/decisions/hide-learning-complexity-from-operator.md
  - docs/wiki/systems/orchestration-and-engine-runtime.md
  - docs/wiki/systems/evaluation-and-anti-hallucination.md
  - docs/wiki/systems/defense-synthesis-and-validation.md
  - docs/wiki/systems/promotion-and-revalidation.md
  - src/redthread/cli/run.py
  - src/redthread/cli/run_help.py
  - src/redthread/cli/run_render.py
  - src/redthread/cli/run_reports.py
  - src/redthread/orchestration/supervisor.py
  - src/redthread/orchestration/graphs/attack_graph.py
  - src/redthread/orchestration/graphs/defense_graph.py
  - src/redthread/core/guardrail_loader.py
  - src/redthread/evaluation/pipeline.py
  - src/redthread/config/settings.py
  - src/redthread/models.py
  - tests/test_run_cli_reports.py
  - tests/test_tap.py
updated_by: pi
updated_at: 2026-05-18
---

# RedThread Simplicity Implementation Plan

## Research question

How should RedThread simplify from product surface through architecture while preserving the core evidence loop?

Target spine:

```text
attack → judge → defend → replay → promotion evidence
```

## Planning status

Phases 0 through 8 are implemented as of 2026-05-18.

The final pass intentionally kept compatibility shims where deletion would be premature. In particular, `defense_deployed` remains as a deprecated compatibility alias for `validated_candidate` until a later docs/API migration can remove or hide it safely.

This page now records the shipped simplicity implementation rather than requesting further phase approval.

## Non-negotiable constraints

- Keep JudgeAgent as owner of confirmed findings.
- Keep weak signals separate from severity truth.
- Keep replay and promotion boundaries explicit.
- Do not copy raw jailbreak prompt bodies into docs, tests, prompts, reports, or artifacts.
- Preserve existing public CLI behavior unless a phase explicitly deprecates or hides it.
- Keep new or touched modules under the repo file-size rule of 200 lines.
- Stop before schema, migration, dependency, or destructive file changes unless approved.

## Current evidence map

### Product surface

- `README.md` frames the product as: find the exploit, judge it, draft the fix, prove what changed.
- `docs/product.md` says RedThread is CLI-first and owns attack generation, precision evaluation, defense synthesis, validation evidence, and bounded self-improvement.
- `src/redthread/cli/run.py` already has a main `redthread run` command, but it exposes many normal and advanced knobs in the same surface.
- `--report-dir` exists, but standard report persistence is optional instead of the default golden path.

### Orchestration surface

- `src/redthread/orchestration/supervisor.py` currently holds supervisor state, node functions, routing, finalization, runtime summary work, and graph construction in one large file.
- `docs/wiki/systems/orchestration-and-engine-runtime.md` says attack workers are parallel, while judge and defense loops are sequential.
- This is acceptable behavior, but the orchestration code should be easier to audit.

### Attack strategy surface

- `src/redthread/orchestration/graphs/attack_graph.py` dispatches algorithms with an explicit PAIR/TAP/Crescendo/MCTS branch.
- PAIR, TAP, Crescendo, and MCTS should stay.
- The simpler target is one small runner registry, not fewer algorithms.

### Evaluation and reporting surface

- `src/redthread/evaluation/pipeline.py` tracks evidence modes, including live judge fallback.
- Fallback paths can preserve continuity, but they must never read as healthy live proof.
- Operator reports should surface evidence mode, fallback reason, uncertainty, and promotion status before debug details.

### Defense and promotion surface

- `docs/DEFENSE_PIPELINE.md` and `docs/wiki/systems/promotion-and-revalidation.md` separate candidate defense work from promotable evidence.
- `src/redthread/orchestration/graphs/defense_graph.py` and `src/redthread/core/guardrail_loader.py` use operator-facing words like deployment and active guardrails.
- The next pass should audit whether wording and runtime behavior make candidate-versus-active status clear enough.

### Settings and model surface

- `src/redthread/config/settings.py` mixes model roles, provider endpoints, algorithm knobs, runtime flags, telemetry, filesystem paths, and auth settings.
- `src/redthread/models.py` is also above the preferred file-size threshold.
- Simplification should preserve environment variable compatibility while splitting responsibilities.

### Test surface

- `tests/test_tap.py` is empty at the time of this plan.
- TAP should receive smoke and regression tests before broad TAP refactors.

## Approved answer ledger

### Q1 — Default report behavior

Decision: `redthread run` writes a standard report by default.

Policy:

- normal default path: `reports/<campaign_id>/`
- dry-run default path: `reports/<campaign_id>/dry-run/`
- `--report-dir` stays as the root override
- direct `--report-md` and `--report-json` exports remain available

Reason: a prompt to write a report is not proof. RedThread's promise is to prove what changed, so the golden path must create an artifact.

Phase: Phase 1.

### Q2 — CLI help tiers

Decision: use three tiers.

Normal visible options:

- `--objective`
- `--system-prompt`
- `--rubric`
- `--personas`
- `--target` / `--target-model`
- `--dry-run`
- `--algorithm`
- `--report-dir`

Advanced visible options:

- `--depth`
- `--width`
- `--branching`
- `--turns`
- `--simulations`
- `--max-budget-tokens`
- `--verbose`
- `--env-file`
- `--report-md`
- `--report-json`

Research controls hidden from normal help:

- `--trace-all`
- `--benchmark-fixture`
- `--persona-weighting-plan`
- `--include-internal-sidecars`

Research controls remain available through `--show-research` and direct flag use.

Phase: Phase 1.

### Q3 — Active guardrail boundary

Decision: only explicitly promoted controls may become active guardrails.

Hierarchy:

1. `candidate_defense` — generated, not validated
2. `validated_candidate` — replay passed, no promotion yet
3. `promotable_evidence` — replay plus utility gate plus operator approval
4. `active_guardrail` — promoted and actively injected

Only `active_guardrail` is eligible for injection. `GuardrailLoader` should read active guardrails only, not candidates.

Phase: Phase 5. Implemented in the Phase 5 pass and finalized in Phase 8 with `validated_candidate` as the canonical report/state key.

### Q4 — Judge and defense parallelization

Decision: judge and defense loops stay sequential for now.

Parallelization is deferred until performance evidence proves a bottleneck. The current threshold is: if attack workers plus N personas plus judge plus defense complete in under five minutes for an operator, judge/defense parallelization is premature.

Phase: after Phase 3, only if performance data justifies it.

### Q5 — Settings profiles

Decision: profiles are approved later, but only as a minimal enum-style surface.

Future profile targets:

- `default` — golden path
- `research` — higher budgets and debug artifacts
- `ci` — dry-run, low-cost, JSON-friendly

Do not build inheritance, per-layer overrides, or schema-versioned profile systems unless a later requirement proves they are needed.

Phase: Phase 6. Implemented with flat environment compatibility and minimal profile overlays.

## Phase 0 — Baseline proof and cut list

### Goal

Create a safe starting point before changing behavior.

### Work

1. Run current focused tests for CLI run, supervisor, runtime truth, evaluation pipeline, defense pipeline, and reporting.
2. Capture current `redthread run --help` output.
3. Capture a sealed dry-run report artifact shape.
4. Capture line counts for target files.
5. Build a cut list of user-facing flags, report fields, and docs that belong in default, advanced, or research surfaces.

### Files likely touched

None unless the user approves writing a baseline note.

### Acceptance criteria

- Baseline commands and results are recorded.
- No runtime behavior changes.
- No docs claim a future simplification has shipped.
- Implementation risks are listed before Phase 1 begins.

### Suggested verification commands

```bash
python3 scripts/wiki_lint.py
pytest tests/test_supervisor.py tests/test_runtime_truth.py tests/test_evaluation_pipeline.py -q
python -m redthread.cli.app run --help
```

Command names may need adjustment during implementation research if the local CLI entrypoint differs.

### 2026-05-18 baseline notes

Observed before implementation:

- `redthread run --help` showed normal, advanced, and research flags in one flat option list.
- `--trace-all` and `--benchmark-fixture` were visible in normal help.
- standard report persistence required `--report-dir`.
- `src/redthread/cli/run.py` was close to the 200-line file limit, so report persistence and help rendering were extracted instead of growing the command file.

## Phase 1 — Golden operator path

### Goal

Make the normal experience one command and one report.

### Proposed behavior

Default operator path:

```bash
redthread run --objective "test this agent" --system-prompt "..."
```

The command should produce or clearly point to one standard report directory without requiring the operator to know internal sidecar concepts.

### Work

1. Define a default report directory policy.
   - Candidate: `reports/<campaign_id>/`.
   - Keep `--report-dir` as an override.
2. Keep advanced flags working, but group or hide research-only flags from the normal help path where safe.
3. Make the terminal summary point to the report path and the evidence class summary.
4. Make the first report page use courtroom shape:
   - claim
   - judge evidence
   - defense candidate
   - replay evidence
   - promotion status
   - next operator action
5. Keep internal sidecars hidden unless advanced/debug mode asks for them.

### Files likely touched

- `src/redthread/cli/run.py`
- `src/redthread/cli/run_render.py`
- `src/redthread/reporting/*`
- `tests/test_cli_run*.py` or new focused CLI tests
- `README.md` after behavior is implemented

### Acceptance criteria

- A normal dry run writes or clearly reports one standard artifact location.
- Existing explicit `--report-dir` still works.
- Hidden/internal sidecars do not appear in the normal report manifest unless requested.
- Terminal output explains evidence mode and degraded runtime status.
- No confirmed finding is created from weak or fallback evidence alone.

### 2026-05-18 implementation notes

Implemented Phase 1 with a small helper extraction:

- `src/redthread/cli/run_reports.py` owns default report persistence for `redthread run`.
- `src/redthread/cli/run_help.py` owns grouped normal/advanced help and on-demand research flag listing.
- `src/redthread/reporting/persistence.py` now accepts `run_mode_subdir` so dry-run standard reports can live under `reports/<campaign_id>/dry-run/`.
- `src/redthread/cli/run.py` now always writes the standard campaign report bundle, while preserving `--report-dir`, `--report-md`, `--report-json`, and hidden internal sidecar behavior.
- `src/redthread/cli/run_render.py` now prints campaign id, runtime mode, runtime status, evidence label summary when available, report path, and transcript path.
- `tests/test_run_cli_reports.py` covers default report writing, dry-run subdirectory behavior, `--report-dir` override behavior, direct export preservation, normal help grouping, and `--show-research`.

Scope intentionally not changed:

- judge and defense loops remain sequential.
- supervisor structure was not refactored.
- attack algorithm dispatch was not changed.
- guardrail activation semantics were not changed.
- settings profiles were not implemented in Phase 1.

## Phase 2 — Evidence vocabulary hardening

### Goal

Make evidence honesty impossible to miss.

### 2026-05-18 implementation notes

Implemented canonical operator evidence vocabulary through `src/redthread/reporting/evidence_labels.py` and `src/redthread/reporting/evidence_summary.py`.

Shipped behavior:

- report bundles and manifests now include `evidence_labels`, `evidence_mode_counts`, and `evidence_uncertainty`
- Markdown reports include an Evidence & Uncertainty section
- terminal summaries include evidence counts and warnings when available
- hero proof judge stage uses fallback/sealed labels when the run is not clean live proof
- tests assert fallback evidence cannot render as clean live proof

Scope intentionally not changed:

- benchmark scoring internals were not rewritten
- weak imported evidence remains a planning signal only
- no raw jailbreak prompt bodies were added to tests or docs

### Work

1. Define one shared vocabulary for:
   - live judge evidence
   - sealed dry-run evidence
   - fallback judge evidence
   - weak detector signal
   - candidate defense
   - promotable defense
   - active guardrail
2. Ensure report builders and terminal renderers use the same labels.
3. Add a short uncertainty block to reports when mixed or fallback evidence appears.
4. Ensure fallback score continuity cannot be rendered as clean live proof.

### Files likely touched

- `src/redthread/evaluation/pipeline.py`
- `src/redthread/reporting/*`
- `src/redthread/cli/run_render.py`
- `docs/ANTI_HALLUCINATION_SOP.md` only after approval
- tests for reporting/evaluation evidence labels

### Acceptance criteria

- Every operator-facing report includes evidence mode counts.
- Fallback evidence includes fallback reason where available.
- Weak detector hints remain marked as signals, not verdicts.
- Tests fail if fallback is rendered as confirmed live evidence.

## Phase 3 — Thin supervisor and stage spine

### Goal

Turn the supervisor into a thin graph builder over small stage nodes.

### 2026-05-18 implementation notes

Implemented by extracting supervisor state, routing, nodes, finalization, and graph construction into smaller modules while keeping `src/redthread/orchestration/supervisor.py` as a compatibility facade.

Shipped behavior:

- existing imports from `redthread.orchestration.supervisor` remain valid
- attack fan-out behavior remains parallel
- judge and defense loop semantics remain sequential
- runtime degraded/error summaries are preserved

### Work

1. Extract `SupervisorState` and reducers.
2. Extract persona generation node.
3. Extract attack fan-out and result collection node helpers.
4. Extract judge loop node.
5. Extract agentic-security review node.
6. Extract defense synthesis node.
7. Extract finalization/runtime-summary builder.
8. Keep graph topology stable unless a separate approval changes behavior.

### Files likely touched

- `src/redthread/orchestration/supervisor.py`
- `src/redthread/orchestration/supervisor_state.py`
- `src/redthread/orchestration/nodes/persona_generation.py`
- `src/redthread/orchestration/nodes/attack_collection.py`
- `src/redthread/orchestration/nodes/judging.py`
- `src/redthread/orchestration/nodes/agentic_security.py`
- `src/redthread/orchestration/nodes/defense_synthesis.py`
- `src/redthread/orchestration/nodes/finalize_campaign.py`
- `tests/test_supervisor.py`
- `tests/test_runtime_truth.py`

### Acceptance criteria

- `supervisor.py` stays under 200 lines.
- New node files stay under 200 lines.
- Existing campaign flow still works.
- Attack fan-out remains parallel.
- Judge and defense semantics do not change unless explicitly approved.
- Runtime degraded/error summaries are unchanged or more explicit.

## Phase 4 — Attack runner registry and TAP safety net

### Goal

Keep all attack algorithms, but remove brittle dispatch and duplicated runtime plumbing.

### 2026-05-18 implementation notes

Implemented a concrete attack runner registry in `src/redthread/core/attack_runner.py` and switched `attack_graph.py` to registry dispatch.

Shipped behavior:

- PAIR, TAP, Crescendo, and MCTS remain addressable
- unknown algorithms fail clearly through registry lookup
- TAP now has dry-run smoke/safety coverage in `tests/test_tap.py`

### Work

1. Add a narrow `AttackStrategyRunner` or registry interface if the existing one is not sufficient for this path.
2. Register PAIR, TAP, Crescendo, and MCTS by algorithm key.
3. Replace explicit if/elif dispatch in `attack_graph.py` with registry lookup.
4. Extract only shared runtime plumbing first.
5. Do not rewrite algorithm internals until smoke tests exist.
6. Add TAP tests before TAP refactor work.

### Files likely touched

- `src/redthread/orchestration/graphs/attack_graph.py`
- `src/redthread/core/attack_runner.py` or existing strategy-runner module
- `src/redthread/core/pair.py`
- `src/redthread/core/tap.py`
- `src/redthread/core/crescendo.py`
- `src/redthread/core/mcts.py`
- `tests/test_tap.py`
- attack graph tests

### Acceptance criteria

- Unknown algorithm still fails clearly.
- All four current algorithms remain addressable.
- TAP has at least smoke coverage for setup, budget/depth handling, and result shape.
- No raw jailbreak prompt bodies are added to tests.
- Attack result metadata keeps strategy lineage.

## Phase 5 — Defense candidate, replay, and promotion boundary

### Goal

Make it clear when a defense is proposed, validated, promotable, or active.

### 2026-05-18 implementation notes

Implemented the runtime boundary that defense synthesis writes `validated_candidate` evidence and guardrail loading injects only scoped `active_guardrail` records.

Shipped behavior:

- defense synthesis indexes validated candidates, not active runtime controls
- `load_scoped_guardrails()` reads structured deployments first and filters to active guardrails with matching model/prompt hash and passed validation
- `defense_deployed` is retained only as a deprecated compatibility alias meaning validated/indexed candidate

### Work

1. Audit current defense wording and runtime status fields.
2. Replace ambiguous operator wording where possible.
   - Prefer `candidate_defense` for generated clauses.
   - Prefer `validated_candidate` when replay passed but promotion is not complete.
   - Reserve `active_guardrail` for explicitly active scoped controls.
3. Check whether sealed dry-run replay can lead to active-looking guardrail injection.
4. If a data model change is required, stop and request approval before schema-like changes.
5. Add tests that sealed evidence cannot be described as live promotion proof.

### Files likely touched

- `src/redthread/orchestration/graphs/defense_graph.py`
- `src/redthread/core/guardrail_loader.py`
- `src/redthread/memory/index.py`
- `src/redthread/core/defense_synthesis.py`
- `src/redthread/core/defense_replay_runner.py`
- `src/redthread/reporting/*`
- defense and promotion tests

### Acceptance criteria

- Operator output cannot confuse candidate persistence with production promotion.
- Live-promotable evidence remains stricter than sealed dry-run evidence.
- Guardrail loading behavior is documented and tested.
- Existing safe defense replay paths still work.

## Phase 6 — Settings and profile simplification

### Goal

Keep environment compatibility while making defaults easier to understand.

### 2026-05-18 implementation notes

Implemented by keeping `RedThreadSettings` as the flat public settings facade and splitting field concerns into small mixins.

Shipped behavior:

- existing `REDTHREAD_` environment names continue to work
- profiles are minimal overlays: `default`, `research`, `ci`
- explicit constructor/env/`.env` values continue to win over profile defaults

### Work

1. Split settings by concern if implementation research confirms it is safe:
   - model roles
   - provider endpoints
   - algorithm budgets
   - runtime/reporting
   - telemetry
   - filesystem paths
2. Preserve `REDTHREAD_` environment variable behavior.
3. Add a simple profile concept only if it removes operator decisions.
   - Candidate profiles: `default`, `research`, `ci`.
4. Avoid adding new config concepts that only move complexity around.

### Files likely touched

- `src/redthread/config/settings.py`
- `src/redthread/config/*`
- config tests
- CLI tests for env overrides

### Acceptance criteria

- Current env vars still work.
- Defaults still support the golden path.
- Advanced algorithm knobs remain available.
- Config docs become shorter, not broader.

## Phase 7 — Product docs, wiki, and operator guidance cleanup

### Goal

Make docs match the simpler product shape after code behavior exists.

### 2026-05-18 implementation notes

Implemented by updating README, product framing, and wiki pages to describe the shipped golden path, evidence vocabulary, and candidate-versus-active guardrail boundary.

Shipped behavior:

- README quickstart now documents default report paths and `--show-research`
- product docs now state that validated candidates are not active guardrails
- wiki decision/system pages reflect implemented behavior only

### Work

1. Update README quickstart around the golden path.
2. Update product docs around courtroom evidence framing.
3. Update wiki system pages with implemented behavior only.
4. Add one operator workflow page if needed.
5. Remove or de-emphasize stale manual sidecar workflows from normal docs.

### Files likely touched

- `README.md`
- `docs/product.md`
- `docs/wiki/index.md`
- relevant `docs/wiki/systems/*`
- relevant `docs/wiki/decisions/*`
- `docs/wiki/log.md`

### Acceptance criteria

- Docs do not claim unimplemented behavior.
- Normal path is obvious.
- Advanced and research paths are clearly labeled.
- Wiki lint passes.

## Phase 8 — Final deletion and deprecation pass

### Goal

Delete or demote complexity that survived earlier phases only for compatibility.

### 2026-05-18 implementation notes

Implemented as a deprecation/demotion pass, not a destructive deletion pass.

Shipped behavior:

- `validated_candidate` is the canonical defense-candidate metadata/report key
- `defense_deployed` remains as a deprecated compatibility alias
- no files, flags, or capabilities were deleted without a separate removal/migration pass

### Work

1. Review flags, artifact fields, and docs that became obsolete.
2. Mark deprecated surfaces with clear migration paths.
3. Delete dead helpers only after tests prove no active use.
4. Keep compatibility shims if deletion would break expected workflows.

### Files likely touched

To be determined after Phases 1-7.

### Acceptance criteria

- No dead default-path docs remain.
- Deprecated paths have migration notes.
- Tests and wiki lint pass.
- No essential RedThread capability was removed.

## Phase order

Implemented order:

1. Phase 0 — baseline proof.
2. Phase 1 — golden operator path.
3. Phase 3 — supervisor extraction.
4. Phase 4 — attack runner registry and TAP tests.
5. Phase 5 — defense/promotion boundary.
6. Phase 6 — settings split.
7. Phase 2 — evidence vocabulary hardening.
8. Phase 7 — docs cleanup.
9. Phase 8 — final deprecation pass.

Deviation: Phase 2 was completed after Phases 3-6 because the initial implementation turn began with the approved architecture slices. The final result still preserves the intended safety outcome: product and report vocabulary now reflect the shipped architecture and defense boundary.

## Completion state

The simplicity plan is complete through Phase 8.

Compatibility items intentionally left for a future cleanup:

- remove or hide `defense_deployed` only after canonical `validated_candidate` consumers are fully documented and migrated
- remove or hide `defense_deployments` only after canonical `defense_validated_candidates` consumers are fully documented and migrated
- continue keeping hidden research flags available unless a separate deprecation decision removes them
- keep advanced algorithms and settings knobs available behind operator/research tiers rather than deleting core capability

## Resolved questions

1. `redthread run` writes `reports/<campaign_id>/` by default.
2. Dry-run reports write under `reports/<campaign_id>/dry-run/`.
3. CLI help uses normal, advanced, and hidden research tiers.
4. Active guardrail injection is reserved for explicitly promoted controls, but implementation is deferred to Phase 5.
5. Judge and defense loops stay sequential until performance data proves a bottleneck.
6. Minimal `default`, `research`, and `ci` profiles are implemented in Phase 6.
7. Fallback, weak, sealed, candidate, promotable, and active states now use canonical evidence vocabulary in operator reports.
8. `defense_deployed` is deprecated as wording, but retained as a compatibility alias for `validated_candidate` until a later migration removes it.
9. `defense_validated_candidates` is the canonical supervisor/runtime count; `defense_deployments` is retained as a compatibility alias.
10. Defense candidate metadata now keeps `deployed` and `active_guardrail` false until explicit promotion.
11. Defense status aliases are centralized in `src/redthread/core/defense_status.py` so canonical fields and deprecated compatibility keys stay mirrored consistently.
12. Phase 9 wording migration now prefers defense-candidate language where no active guardrail is implied. API names such as `DeploymentRecord` remain compatibility debt for a later breaking migration.

## Phase 10 — Operator proof UX

### Goal

Make the default report answer the operator's first three questions before exposing detailed artifacts:

1. what happened
2. why trust it
3. what should happen next

### 2026-05-18 implementation notes

Implemented by adding `src/redthread/reporting/proof_readout.py` and placing its sections at the top of `operator-report.md`.

Shipped behavior:

- Markdown reports now start with Executive Summary, Why Trust This Report, and What To Do Next
- the summary includes confirmed finding count, run count, attack success rate, average JudgeAgent score, evidence mode, and promotion state
- the trust section names JudgeAgent as the owner of confirmed findings, keeps detector hints weak, and prints the attack → judge → defense candidate → replay → benign check → CI proof path
- next actions distinguish finding review from promotion approval and preserve explicit replay/promotion gates
- JSON artifact shape remains unchanged for compatibility

Scope intentionally not changed:

- no UI was added
- no promotion decision was automated
- no research/debug sidecars were exposed by default

## Phase 11 — Promotion workflow hardening

### Goal

Make the defense promotion ladder explicit and fail closed:

`candidate_defense → validated_candidate → promotable_defense → active_guardrail`

### 2026-05-18 implementation notes

Implemented by extending canonical defense status helpers and promotion validation artifacts.

Shipped behavior:

- `src/redthread/core/defense_status.py` now owns the state names and metadata helpers for inactive candidates and active guardrails
- promotion validation writes `promotion_state_by_trace` and `promotion_evidence_mode_by_trace`
- accepted live replay records with complete utility-gate evidence are marked `promotable_defense` during validation
- records written to production memory by explicit promotion are marked `active_guardrail`, `active_guardrail=true`, and `deployed=true`
- sealed dry-run replay evidence remains `validated_candidate` and cannot promote by accident
- `live_validation_error` fails closed and cannot promote by accident

Scope intentionally not changed:

- `DeploymentRecord` remains the compatibility type name
- promotion is still operator-triggered; no automatic promotion loop was added
- live adapter behavior was not broadened

## Phase 12 — Promotion proof readout

### Goal

Make promotion evidence readable at the CLI, not just buried in JSON artifacts.

Operators should see:

1. whether promotion wrote an `active_guardrail`
2. the full defense ladder
3. state counts by promotion state
4. per-trace state plus evidence mode
5. why weak, missing, or failed traces were blocked

### 2026-05-18 implementation notes

Implemented by adding `src/redthread/research/promotion_readout.py` and wiring it into:

- `redthread research promote`
- `redthread research promote-inspect`

Shipped behavior:

- successful promotion prints `active_guardrail written: N`
- dry-run promotion prints `dry_run: no production memory write`
- failed promotion prints `blocked: no active guardrail was written`
- both promote surfaces show the ladder `candidate_defense → validated_candidate → promotable_defense → active_guardrail`
- both promote surfaces show state counts, such as `promotable_defense=1` or `validated_candidate=1`
- trace rows show `state=<state>` and `evidence=<evidence_mode>`
- promoted traces visibly bridge from `promotable_defense` to `active_guardrail`

Scope intentionally not changed:

- JSON artifact compatibility was preserved
- no automatic promotion approval was added
- no UI beyond CLI readouts was added

## Phase 13 — Runtime active-guardrail audit proof

### Goal

Make runtime guardrail injection auditable without relying on raw prompt text.

Operators and tests should be able to prove:

1. only `active_guardrail` records are eligible for runtime injection
2. validated candidates are skipped
3. skipped versus injected decisions are written as audit events
4. audit events name trace IDs and clause hashes, not raw clause text
5. prompt scope remains explicit through `target_model` and `prompt_hash`

### 2026-05-18 implementation notes

Implemented by adding structured, non-secret audit proof to `GuardrailLoader` and a structured active-record lookup to `MemoryIndex`.

Shipped behavior:

- `MemoryIndex.load_scoped_guardrail_records()` returns only passed `active_guardrail` records matching `target_model` and prompt hash
- `GuardrailLoader` writes `logs/guardrail_audit.jsonl` events with `action`, `active_guardrail_count`, `active_trace_ids`, `clause_hashes`, `target_model`, `prompt_hash`, and `source`
- audit events no longer need raw `clauses` to prove what happened
- `GuardrailLoader.last_audit` keeps the latest injection decision available to runtime callers and tests
- tests prove active records inject, validated candidates skip, and skip events are auditable

Scope intentionally not changed:

- runtime injection still happens only from explicit `active_guardrail` records
- no automatic promotion was added
- legacy markdown fallback remains for older memory files, but structured deployment records stay authoritative

## Sources

- [../../../README.md](../../../README.md)
- [../../product.md](../../product.md)
- [../../TECH_STACK.md](../../TECH_STACK.md)
- [../../PHASE_REGISTRY.md](../../PHASE_REGISTRY.md)
- [../../AGENT_ARCHITECTURE.md](../../AGENT_ARCHITECTURE.md)
- [../../DEFENSE_PIPELINE.md](../../DEFENSE_PIPELINE.md)
- [../../ANTI_HALLUCINATION_SOP.md](../../ANTI_HALLUCINATION_SOP.md)
- [../decisions/simplicity-spine-and-golden-path.md](../decisions/simplicity-spine-and-golden-path.md)
- [../decisions/hide-learning-complexity-from-operator.md](../decisions/hide-learning-complexity-from-operator.md)
- [../systems/orchestration-and-engine-runtime.md](../systems/orchestration-and-engine-runtime.md)
- [../systems/evaluation-and-anti-hallucination.md](../systems/evaluation-and-anti-hallucination.md)
- [../systems/defense-synthesis-and-validation.md](../systems/defense-synthesis-and-validation.md)
- [../systems/promotion-and-revalidation.md](../systems/promotion-and-revalidation.md)
- [../../../src/redthread/cli/run.py](../../../src/redthread/cli/run.py)
- [../../../src/redthread/cli/run_help.py](../../../src/redthread/cli/run_help.py)
- [../../../src/redthread/cli/run_render.py](../../../src/redthread/cli/run_render.py)
- [../../../src/redthread/cli/run_reports.py](../../../src/redthread/cli/run_reports.py)
- [../../../src/redthread/orchestration/supervisor.py](../../../src/redthread/orchestration/supervisor.py)
- [../../../src/redthread/orchestration/graphs/attack_graph.py](../../../src/redthread/orchestration/graphs/attack_graph.py)
- [../../../src/redthread/orchestration/graphs/defense_graph.py](../../../src/redthread/orchestration/graphs/defense_graph.py)
- [../../../src/redthread/core/defense_status.py](../../../src/redthread/core/defense_status.py)
- [../../../src/redthread/core/guardrail_loader.py](../../../src/redthread/core/guardrail_loader.py)
- [../../../src/redthread/memory/index.py](../../../src/redthread/memory/index.py)
- [../../../src/redthread/research/promotion.py](../../../src/redthread/research/promotion.py)
- [../../../src/redthread/research/promotion_readout.py](../../../src/redthread/research/promotion_readout.py)
- [../../../src/redthread/research/promotion_inspection.py](../../../src/redthread/research/promotion_inspection.py)
- [../../../src/redthread/evaluation/pipeline.py](../../../src/redthread/evaluation/pipeline.py)
- [../../../src/redthread/config/settings.py](../../../src/redthread/config/settings.py)
- [../../../src/redthread/reporting/exporters.py](../../../src/redthread/reporting/exporters.py)
- [../../../src/redthread/reporting/proof_readout.py](../../../src/redthread/reporting/proof_readout.py)
- [../../../src/redthread/models.py](../../../src/redthread/models.py)
- [../../../tests/test_run_cli_reports.py](../../../tests/test_run_cli_reports.py)
- [../../../tests/test_tap.py](../../../tests/test_tap.py)
