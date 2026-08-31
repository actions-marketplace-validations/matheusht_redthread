# RedThread PyRIT + Defense Framework Fit Review

Date: 2026-05-24
Branch: `research/pyrit-defense-framework-fit`
Scope: research only. No code, dependency, CLI, or PR change recommended here.

## Bottom line

**Approve research. Defer integration.**

RedThread should not become a wrapper around PyRIT, NeMo Guardrails, Guardrails AI, LLM Guard, any-guardrail, or benchmark suites.

Use outside projects only when they strengthen RedThread’s existing proof spine:

```text
attack → judge → defend → replay → promotion evidence
```

## Fit decision

| Area | Decision | Why |
| --- | --- | --- |
| PyRIT target layer | Keep, harden | RedThread already uses a thin PyRIT target wrapper. This is useful plumbing. |
| PyRIT orchestrators/executors | Do not adopt wholesale | RedThread owns attack orchestration, evidence, and promotion semantics. |
| PyRIT converters | Mine ideas only | Useful for attack variation and normalization, but should not become user-facing complexity. |
| PyRIT scorers | Weak signals only | JudgeAgent remains authority for confirmed findings. |
| PyRIT memory | Non-canonical only | RedThread `MemoryIndex` / promotion records remain source of truth. |
| Guardrail runtimes | Defer | Runtime adoption adds policy-language and dependency weight. |
| Guardrail detectors | Shadow hints only | Helpful for triage, not enough for promotion evidence. |
| Benchmarks | Best near-term value | Use as labeled replay/seed corpus, not leaderboard truth. |
| CoP | Keep research-only | Early signal is promising, but sample is too small for default behavior. |

## Repo facts used

- `pyproject.toml` pins `pyrit==0.12.0`.
- `src/redthread/pyrit_adapters/client.py` is a thin async wrapper around PyRIT `PromptChatTarget`.
- `src/redthread/pyrit_adapters/runtime.py` initializes PyRIT `CentralMemory` with SQLite and builds OpenAI-compatible targets.
- `src/redthread/core/defense_synthesis.py` already owns isolate → classify/generate → validate → deploy candidate records.
- `src/redthread/core/defense_assets.py` already defines guardrail writing rules and sealed benign utility checks.
- `docs/DEFENSE_PIPELINE.md` defines the ladder: `candidate_defense → validated_candidate → promotable_defense → active_guardrail`.
- Current CoP result to keep as research signal only: 5 runs → 3 confirmed jailbreaks, 2 partials, 0 dead failures.

## External findings

### PyRIT

PyRIT’s public docs expose broad surfaces: attack executors, converters, prompt targets, scorers, and memory. Current docs also describe target capabilities / requirements and many target types.

Useful parts:

1. **Target contracts**
   - RedThread can learn from PyRIT `TargetRequirements` / capability checks.
   - Good for preventing silent mismatch in multi-turn, system-prompt, image, or HTTP target support.

2. **Converter patterns**
   - Useful as inspiration for controlled prompt variation.
   - Must remain behind RedThread strategy logic.

3. **Scorer contracts**
   - Useful as optional secondary signals.
   - Must not replace JudgeAgent.

Reject:

- PyRIT orchestrator rewrite.
- PyRIT scorer as finding authority.
- PyRIT memory as promotion truth.
- New user-facing PyRIT modes or flags.

Version note: external PyRIT docs may be ahead of pinned `pyrit==0.12.0`. Any future adoption must verify the exact pinned API first.

### Guardrail frameworks

**NeMo Guardrails** offers programmable input/dialog/output/retrieval/execution rails and a guardrails runtime. Good idea source. Too heavy as RedThread runtime right now.

**Guardrails AI** focuses on input/output guards, validators, and structured generation. Useful validator taxonomy. Runtime/server adoption is too much surface.

**LLM Guard** provides prompt/output scanners for prompt injection, secrets, toxicity, code, regex, sensitive data, and related risks. Good as a shadow detector. Bad as default enforcement.

**any-guardrail** gives a unified API over guardrail models such as Llama Guard / ShieldGemma-like providers. Useful abstraction idea. Bad default dependency now.

Decision: mine their taxonomies, benign utility checks, and clause examples. Do not adopt them as runtime policy engines.

### Benchmarks and defense-eval repos

Best value comes from benchmark corpora and evaluation ideas:

- **JailbreakBench**: behavior dataset, jailbreak strings, defense algorithms, jailbreak/refusal judge datasets.
- **MT-JailBench**: multi-turn attack structures, budget metadata, reproducible run logs.
- **Panda Guard / PandaBench**: attacker/defender/judge framing and defense algorithm catalog.
- **SoK4JailbreakGuardrails**: processed datasets and guardrail evaluation coverage across attacks and benign inputs.

Use them as source material for labeled replay seeds and benign utility probes.

Do not use benchmark scores as RedThread truth.

## Impact, leverage, and improvement surface

PyRIT should impact only RedThread's target interaction seam. That seam includes `RedThreadTarget`, target factories, shared send helpers, execution metadata, canary containment, and controlled live adapter behavior. It should not change LangGraph orchestration, PAIR/TAP/Crescendo/MCTS logic, JudgeAgent authority, defense synthesis, replay promotion, or canonical memory.

The useful leverage is provider and transport plumbing: prompt target abstractions, OpenAI-compatible endpoints, rate-limit/retry behavior, target capability metadata, converter modality contracts, and memory-backed conversation mechanics. RedThread should consume these as hidden adapter capabilities, not expose a broad PyRIT product mode.

The improvement goal is practical reliability, not feature volume:

| Improvement | Meaning in RedThread | Boundary |
| --- | --- | --- |
| Target reach | Add or harden target support through existing factories and `TargetBackend` paths. | No new user-facing PyRIT orchestration mode. |
| Send reliability | Normalize errors, retries, conversation IDs, and execution records at one boundary. | Do not bypass canary containment or live authorization seams. |
| Capability honesty | Fail early when a target cannot support required multi-turn, JSON, multimodal, or history behavior. | Do not infer proof from PyRIT capability labels alone. |
| Evidence quality | Preserve live/blocked/failed/replayed metadata for operator inspection. | JudgeAgent and replay evidence remain the source of truth. |
| Lower adapter drag | Reuse stable PyRIT target/converter contracts where they remove custom code. | Do not import PyRIT memory, scorers, or attacks into canonical RedThread semantics. |

Decision metric: the adapter change is acceptable only when it removes local plumbing, improves evidence truth, or adds target reach without adding a second orchestration/evaluation/memory system.

## Implementation planning handoff

Plan the next implementation as a bounded adapter-hardening tranche:

1. Add a RedThread-owned target capability contract that maps PyRIT 0.12 `TargetCapabilities` into stable RedThread fields.
2. Gate algorithm paths against that contract before sends that need multi-turn, JSON response mode, multimodal pieces, or editable history.
3. Keep all sends flowing through `send_with_execution_metadata()` / `RedThreadTarget.send()` so canary containment, live authorization, and execution records stay intact.
4. Add optional, allowlisted converter adapters only behind existing attack strategy internals. Do not add CLI flags until there is replay proof that operators need them.
5. Add version-drift tests for `pyrit==0.12.0` and document the `0.13.0` migration risk where `TargetConfiguration` replaces `TargetCapabilities`.

Acceptance test: existing attack, judge, sandbox, defense replay, canary containment, and live execution truth tests still pass, and new capability-gate tests prove unsupported target modes fail before provider calls.

## Recommended adoption path

1. **Write an External Evidence Intake Contract**
   - Define labels like `benchmark_seed`, `shadow_detector_signal`, `confirmed_finding`, `validated_candidate`, `regression_case`.
   - State what can affect replay and what can affect promotion.
   - State that external labels never become confirmed findings by themselves.

2. **Add benchmark seeds only after license/safety review**
   - Start with metadata and behavior categories.
   - Avoid raw harmful prompt bodies in docs and tests.
   - Normalize into existing replay/evidence rules.

3. **Harden PyRIT target assumptions**
   - Check whether the current target supports needed capabilities before multi-turn or system-prompt-dependent attacks.
   - Keep this hidden under existing engine behavior.

4. **Improve guardrail clause rubrics**
   - Borrow taxonomy ideas from guardrail frameworks.
   - Keep RedThread’s own clause format and benign utility gate.

5. **Keep CoP behind research proof**
   - Run controlled A/B tests before defaulting it.
   - Promotion remains judge + replay + utility gated.

## Hard rejects

- Wholesale PyRIT orchestrator/executor migration.
- External scanner wrapper mode.
- New dashboard.
- More default CLI flags for this research.
- More agents.
- More evidence states beyond a clearly documented intake label set.
- External scorer replacing JudgeAgent.
- External memory replacing RedThread promotion memory.
- Benchmark leaderboard claims as product proof.
- Guardrail framework as default runtime enforcement.
- CoP as default before controlled A/B proof.

## Advisor review

- `redthread-cto`: available. Verdict: approve with changes. Keep PyRIT as plumbing. Reject wrapper/platform expansion.
- Senior AI Engineer agent: not available by that name in the agent list.
- `plan-ceo-review`: available. Verdict: approve with changes. Lead with evidence quality, not tool coverage.
- `office-hours`: available. Recommendation matched: avoid wholesale adoption; mine datasets, contracts, and templates. Main blind spots were PyRIT version drift, benchmark mismatch, judge authority confusion, memory authority confusion, over-refusal risk, and CoP scope creep.

## Source links

- PyRIT API docs: https://microsoft.github.io/PyRIT/api/
- PyRIT prompt targets: https://microsoft.github.io/PyRIT/api/pyrit-prompt-target/
- NeMo Guardrails: https://github.com/NVIDIA/NeMo-Guardrails/
- Guardrails AI: https://github.com/guardrails-ai/guardrails
- LLM Guard: https://github.com/protectai/llm-guard
- any-guardrail: https://github.com/mozilla-ai/any-guardrail
- JailbreakBench: https://github.com/JailbreakBench/jailbreakbench
- MT-JailBench: https://github.com/SafetyArena/mt-jailbench
- Panda Guard: https://github.com/Beijing-AISI/panda-guard
- SoK4JailbreakGuardrails: https://github.com/xunguangwang/SoK4JailbreakGuardrails
