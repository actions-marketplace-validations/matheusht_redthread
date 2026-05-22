# CoP (Composition of Principles) — Implementation Note

**Date:** 2026-05-21
**Branch:** `feat/cop-strategy-composition`
**Paper:** arXiv:2506.00781 — "CoP: Composition of Principles for Agentic Red-Teaming"
**Status:** Implemented, A/B ready

## What

Replaced from-scratch strategy generation with principle composition. Instead of selecting one atomic strategy per turn, `--cop` composes 2-3 persuasion principles into a single strategy using AND/THEN/WITHIN operators.

## Files Changed

| File | Change |
|------|--------|
| `src/redthread/core/cop.py` | NEW — 10 principles, 3 operators, `generate_cop_strategies()` |
| `src/redthread/config/settings_groups.py` | Added `use_cop: bool` to `AlgorithmBudgetSettings` |
| `src/redthread/cli/run.py` | Added `--cop` flag + wiring through `_apply_run_overrides()` |
| `src/redthread/core/mcts_helpers.py` | Added `use_cop` param to `derive_strategies()`, delegates to CoP |
| `src/redthread/core/mcts.py` | Passes `self.settings.use_cop` at call site |
| `src/redthread/core/crescendo.py` | Same |
| `src/redthread/personas/generator.py` | Same |

## Design Decisions

1. **Single flag, all algorithms.** `--cop` affects MCTS expansion, Crescendo narrative policy, and persona generation (`allowed_strategies`). One flag controls all 4 attack paths — no per-algorithm gating needed.

2. **`derive_strategies()` stays the public API.** Callers pass `use_cop=...` — they don't need to know about CoP. The SRP separation is clean: CoP lives in `cop.py`, `mcts_helpers.py` just delegates.

3. **10 principles, 3 operators.** Principles map directly to existing `PsychologicalTrigger` enum values plus 5 new ones (novelty, commitment, liking, info asymmetry, role fluidity). Operators: AND (simultaneous), THEN (sequence), WITHIN (nesting).

4. **Output is `list[str]` — same shape as atomic strategies.** Attack loops (PAIR/TAP/MCTS/Crescendo) consume strategies as plain strings. No loop changes needed.

5. **`--dry-run` still works.** CoP strategy generation is deterministic (no LLM calls), so dry-run mode skips live interaction as before.

## How to A/B

```
# Control (atomic strategies)
redthread run --algorithm mcts \
  --objective "customer data extraction via authority impersonation" \
  --system-prompt "You are a customer support agent..." \
  --target llama3.2:3b

# Treatment (composed strategies)
redthread run --algorithm mcts --cop \
  --objective "customer data extraction via authority impersonation" \
  --system-prompt "You are a customer support agent..." \
  --target llama3.2:3b
```

Compare: ASR, time to first jailbreak, total tokens, branches explored.

## Verification

`make test` — 611 passed, 1 skipped (identical to pre-change, no regressions).

## Next Steps (when resuming)

1. Run control campaign without `--cop` (atomic strategies)
2. Run treatment campaign with `--cop` (composed strategies)
3. Compare ASR, time to first jailbreak, total tokens, branches explored
4. If CoP outperforms, consider making it the default in a future PR
5. Optional: split the 10 oversized files (>200 lines) — mechanical extraction
6. Optional: add live smoke test + offline dry-run (~65 lines)
