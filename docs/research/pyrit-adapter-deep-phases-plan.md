# PyRIT Adapter Deep Phases Implementation Plan

Date: 2026-05-28
Status: Phases 1–6 implemented through bounded adapter hardening and converter planning. Converter runtime behavior remains deferred.

## Approved choices

- First implementation slice: capability gates.
- Converter policy: keep converters out of the first slice. Revisit later as a separate text-only allowlist after gates land and tests prove value.
- Unsupported capability failures: logs/execution records only. Do not add them to operator report summaries in this phase.

## Architecture goal

Make RedThread more honest and reliable at the target boundary without changing what RedThread is. PyRIT remains infrastructure plumbing. RedThread remains the owner of orchestration, attacks, JudgeAgent scoring, defense synthesis, replay, promotion, and canonical memory.

The adapter should answer one question before a provider call runs: can this target support the behavior RedThread is about to request?

## Phase 0 — Baseline lock

Purpose: prove current behavior before changing the seam.

Work:
- Snapshot current adapter behavior in tests.
- Confirm `pyrit==0.12.0` is installed and exposes `TargetCapabilities`.
- Confirm direct text sends still work through `RedThreadTarget.send()` and `send_with_execution_metadata()`.
- Confirm canary containment still blocks before legacy fallback paths.

Files:
- `tests/test_target_execution_records.py`
- `tests/test_canary_send_helper.py`
- new `tests/test_pyrit_capability_version_guard.py`

Acceptance:
- Existing focused tests pass.
- Version guard fails clearly if PyRIT's capability API changes.

## Phase 1 — RedThread-owned capability contract

Purpose: avoid leaking PyRIT API churn into the rest of RedThread.

Work:
- Add `src/redthread/pyrit_adapters/capabilities.py`.
- Define `RedThreadTargetCapabilities` with stable fields:
  - `supports_multi_turn`
  - `supports_multi_message_pieces`
  - `supports_json_output`
  - `supports_json_schema`
  - `supports_editable_history`
  - `input_modalities`
  - `output_modalities`
- Define `CapabilityRequirement` for requested behavior.
- Add `from_pyrit_target(target)` mapper for PyRIT 0.12 `target.capabilities`.
- Add a safe fallback for fake targets in tests: default text-only, no advanced support unless explicit.

Acceptance:
- Mapping tests pass using fake targets and local PyRIT target instances.
- File remains below 200 lines.
- No production send behavior changes yet.

## Phase 2 — Preflight gate at the adapter seam

Purpose: fail before provider execution when RedThread asks for unsupported behavior.

Work:
- Add a small preflight function in the adapter layer.
- Keep default text sends unchanged.
- Add optional requirement input to `RedThreadTarget.send()` only if needed by current call sites. Prefer a backward-compatible keyword with default `None`.
- Ensure unsupported capability errors occur before `_target.send_prompt_async()`.
- Ensure failure is recorded through existing execution records when execution metadata exists.

Files:
- `src/redthread/pyrit_adapters/client.py`
- `src/redthread/pyrit_adapters/capabilities.py`
- `tests/test_pyrit_target_capabilities.py`

Acceptance:
- Unsupported JSON/multi-turn/multimodal requirement fails before provider call.
- Supported requirement allows the send.
- Existing callers need no change for normal text sends.

## Phase 3 — Factory and target construction alignment

Purpose: make capabilities visible without adding user-facing complexity.

Work:
- Inspect target construction in `runtime.py` and `factories.py`.
- If needed, pass known custom capabilities into PyRIT target construction for local/OpenAI-compatible targets where PyRIT defaults are wrong.
- Keep settings unchanged unless a hard blocker appears.
- Do not add CLI flags.

Files:
- `src/redthread/pyrit_adapters/runtime.py`
- `src/redthread/pyrit_adapters/factories.py`
- `tests/test_pyrit_target_capabilities.py`

Acceptance:
- OpenAI-compatible targets expose normalized capabilities.
- Ollama/llama.cpp-compatible targets remain text-send compatible.
- No change to public CLI surface.

## Phase 4 — Logs-only failure evidence

Purpose: preserve operator truth without expanding reports.

Work:
- On unsupported capability failure, record:
  - seam
  - role
  - model name
  - requested capability
  - target capability snapshot
  - `success=False`
  - pre-provider-call error reason
- Keep this in execution records/logs only.
- Do not add report summary sections.

Files:
- `src/redthread/pyrit_adapters/client.py`
- `src/redthread/pyrit_adapters/execution_records.py` only if current metadata shape cannot carry this cleanly.
- Tests under execution record coverage.

Acceptance:
- Logs show unsupported capability failure.
- Operator report summary remains unchanged.
- No provider call is made on fail-closed preflight.

## Phase 5 — Regression sweep

Purpose: prove the adapter hardening did not break RedThread's core spine.

Focused tests:
- `tests/test_target_execution_records.py`
- `tests/test_canary_send_helper.py`
- `tests/test_canary_containment.py`
- `tests/test_live_execution_truth_smoke.py`
- `tests/test_agentic_replay_promotion.py`
- `tests/test_defense_replay_authorization.py`
- new capability tests

Full command:

```bash
PYTHONPATH=src .venv/bin/pytest
```

Acceptance:
- Focused tests pass before full suite.
- Full suite pass or any failure is unrelated and documented.

## Phase 6 — Post-gate converter planning only

Purpose: decide later whether converters are worth adding.

Work after gates land:
- Review replay evidence and operator need.
- If useful, design a separate text-only converter allowlist hidden behind existing attack strategy internals.
- Allowlist only deterministic, text-in/text-out converters.
- No CLI flags unless operator evidence proves need.

Rejected for now:
- multimodal converters
- converter chains as user-facing modes
- PyRIT orchestrators
- PyRIT scorer authority
- PyRIT memory as RedThread truth

## Threats and mitigations

| Risk | Why it matters | Mitigation |
| --- | --- | --- |
| Direct PyRIT send bypass | Can skip canary/live controls. | Keep one shared send boundary and test no unsupported send reaches provider. |
| PyRIT version drift | 0.13 replaces `TargetCapabilities` with `TargetConfiguration`. | RedThread-owned contract plus version guard tests. |
| Capability overtrust | Capability support is not safety proof. | Use only for preflight, never promotion or JudgeAgent truth. |
| Evidence noise | Operator reports can get noisy. | Logs-only unsupported failures in this phase. |
| Converter creep | Adds feature surface before proof. | Defer until after gates and design as separate allowlist. |

## Detailed design

### Capability model

The RedThread contract should be boring and stable. It should not expose PyRIT classes outside `pyrit_adapters`.

```python
@dataclass(frozen=True)
class RedThreadTargetCapabilities:
    supports_multi_turn: bool = False
    supports_multi_message_pieces: bool = False
    supports_json_output: bool = False
    supports_json_schema: bool = False
    supports_editable_history: bool = False
    input_modalities: frozenset[frozenset[str]] = frozenset({frozenset({"text"})})
    output_modalities: frozenset[frozenset[str]] = frozenset({frozenset({"text"})})
```

The requirement object should describe only what the caller is about to use:

```python
@dataclass(frozen=True)
class CapabilityRequirement:
    requires_multi_turn: bool = False
    requires_multi_message_pieces: bool = False
    requires_json_output: bool = False
    requires_json_schema: bool = False
    requires_editable_history: bool = False
    input_modalities: frozenset[str] = frozenset({"text"})
    output_modalities: frozenset[str] = frozenset({"text"})
```

Validation should return a structured result instead of only raising. That keeps tests and logs clean.

```python
@dataclass(frozen=True)
class CapabilityCheck:
    supported: bool
    reason: str
    missing: tuple[str, ...] = ()
```

Raise only at the final preflight boundary, with a dedicated exception such as `UnsupportedTargetCapabilityError`.

### Default behavior

A normal text-only send should not need a requirement argument. If no requirement is passed, the adapter uses the default text requirement. This protects existing call sites.

Target fakes in tests should be treated as text-only unless they provide a `capabilities` attribute. This avoids false confidence from test doubles that accidentally look fully capable.

### Where the gate lives

The gate belongs inside `RedThreadTarget.send()` before message construction and before `_target.send_prompt_async()`.

Order:
1. Resolve conversation ID.
2. Apply canary containment.
3. Run live execution interception.
4. Run capability preflight.
5. Build PyRIT message.
6. Send through PyRIT.
7. Record success or failure.

This preserves current safety order while adding the capability check before the provider call.

### Why not put the gate in algorithms

Algorithms should not know PyRIT details. PAIR, TAP, Crescendo, and MCTS can request behavior through a generic requirement when needed, but the adapter decides whether the concrete target can honor it. This keeps separation of concerns intact.

## Call-site strategy

### First pass: adapter-only

Implement Phase 1 and Phase 2 without touching algorithms. Default text requirements cover current behavior. Tests prove unsupported advanced requirements fail when passed directly to the adapter.

### Second pass: targeted call sites only if needed

Only add requirements at call sites that truly depend on a capability:

| Call site type | Requirement | Add now? |
| --- | --- | --- |
| Basic target send | text input/output | default only |
| Judge JSON response request | JSON output if metadata requests JSON | only if current path uses PyRIT JSON mode |
| Multi-turn attack path | multi-turn | only if the path depends on target-side history |
| Crescendo client-side history | no target requirement if prompt is flattened | no |
| Multimodal future path | input/output modalities | not now |
| Editable-history path | editable history | not now |

This prevents fake precision. Gates should protect actual behavior, not imagined future behavior.

## Logging design

Unsupported capability failures stay in execution records/logs only.

Recommended metadata shape inside existing execution metadata:

```python
metadata={
    "capability_preflight": {
        "supported": False,
        "missing": ["json_output"],
        "reason": "target does not support JSON output",
        "target_capabilities": {...},
    }
}
```

Do not add report summary fields. Do not add a new evidence class unless current execution records cannot represent pre-provider failure clearly.

## Test matrix

| Test | Purpose | Provider call allowed? |
| --- | --- | --- |
| maps_pyrit_012_capabilities | PyRIT 0.12 mapper works | no |
| defaults_fake_target_to_text_only | test doubles do not get advanced support by accident | no |
| allows_default_text_send | backward compatibility | fake only |
| blocks_json_when_unsupported | fail before provider call | no |
| blocks_multimodal_when_unsupported | fail before provider call | no |
| records_preflight_failure | logs-only failure truth | no |
| preserves_canary_first | canary block still wins before capability checks where relevant | no |
| version_guard_target_capabilities | catches PyRIT 0.13-style breaking change | no |
| existing_execution_records | no regression | fake only |

## Migration notes for PyRIT 0.13+

PyRIT 0.13 introduces `TargetConfiguration`, replacing direct use of `TargetCapabilities` in public docs and release notes. RedThread should not upgrade in this tranche.

When upgrade work happens later:
1. Keep `RedThreadTargetCapabilities` unchanged.
2. Add `from_pyrit_configuration()` next to `from_pyrit_target()`.
3. Support both APIs during a migration window if practical.
4. Update version guard tests to assert the accepted API shape.
5. Run full adapter and replay regression before accepting the upgrade.

## Implementation sequencing

### Commit 1 — tests and contract

- Add capability model and mapper.
- Add mapping and version guard tests.
- No call-site behavior changes.

### Commit 2 — adapter preflight

- Add requirement validation.
- Add preflight to `RedThreadTarget.send()` with backward-compatible default.
- Add no-provider-call tests.

### Commit 3 — logs-only failure metadata

- Attach preflight failure detail to execution metadata or error record.
- Prove it does not touch operator summaries.

### Commit 4 — regression and docs

- Run focused tests.
- Run full tests if focused passes.
- Update this plan with final implementation notes if behavior changes during build.

## Rollback plan

Rollback should be simple because the change is additive.

- Remove `capabilities.py`.
- Remove optional requirement handling from `RedThreadTarget.send()`.
- Remove capability tests.
- Keep previous docs/research notes if useful, but mark implementation deferred.

No schema migration, dependency upgrade, or CLI surface should exist, so rollback should not touch user data or operator workflows.

## Open questions

No blocking questions right now.

Non-blocking items to inspect during implementation:
- whether any current JudgeAgent path actually requests PyRIT JSON mode
- whether current multi-turn algorithms rely on target-side memory or only client-side flattened prompts
- whether execution metadata can carry capability preflight details without changing `ExecutionRecord`

## Implementation completion notes

Phases 1–4 are implemented in the PyRIT adapter seam. The implementation added a RedThread-owned capability contract, adapter preflight checks, conservative runtime capability construction for local OpenAI-compatible backends, and logs-only unsupported capability metadata.

Phase 5 is complete: focused checks and the full test suite passed.

Phase 6 is complete as planning only. Converter runtime behavior remains intentionally unimplemented. The follow-up plan is `docs/research/pyrit-text-converter-allowlist-plan.md`.

## Done criteria

Complete for this tranche. Any future converter work needs separate approval and should stay behind a small deterministic text-only allowlist.
