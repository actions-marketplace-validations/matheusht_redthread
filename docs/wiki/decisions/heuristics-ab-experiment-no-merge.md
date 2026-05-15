---
title: Heuristics A/B Experiment No-Merge Decision
type: decision
status: accepted
summary: Hidden hand-written routing heuristics failed the controlled A/B proof and should not be merged or enabled by default.
source_of_truth:
  - docs/wiki/decisions/hide-learning-complexity-from-operator.md
  - docs/wiki/research/tool-technology-slice-16-adaptive-persona-weighting.md
  - docs/wiki/research/tool-technology-slice-17-persona-weighting-report-artifacts.md
  - session artifact: reports/heuristics-ab/comparison-latest.json
updated_by: codex
updated_at: 2026-05-15
---

# Heuristics A/B Experiment No-Merge Decision

## Decision

Do **not** merge or enable the hidden hand-written heuristic routing experiment as product behavior.

The experiment branch may remain archived as failed experiment evidence, but the implementation should not enter the normal runtime path unless a later redesign proves a clear lift under valid A/B gates.

## Context

RedThread tested a hidden heuristics proof pass for attack exploration and defense replay ordering. The intended invariant was:

> Heuristics guide. JudgeAgent decides. Replay proves. Promotion gates approve. Operator stays simple.

This matched the existing adaptive-learning direction: learning and weak telemetry can guide exploration, but they cannot create findings, weaken JudgeAgent, bypass replay, or add normal operator complexity.

## A/B result

The latest valid comparison used matching scope gates:

- same objective
- same target
- same algorithm: `mcts`
- same attacker model: `dolphin-llama3:8b`
- same target model: `llama3.2:3b`
- same judge model: `gpt-4o-mini`
- same rubric: `authorization_bypass`
- same success threshold: `3.5`
- same persona count: `3`
- same replay mode: `live`
- same total runs: `3`

Observed result:

| Metric | Baseline | Heuristic | Outcome |
| --- | ---: | ---: | --- |
| Confirmed findings | 1 | 0 | baseline better |
| Attack success rate | 33.3% | 0.0% | baseline better |
| Average JudgeAgent score | 2.67 | 1.00 | baseline better |
| False-positive proxy count | 2 | 3 | heuristic worse |
| Target call count | 56 | 69 | heuristic worse |
| Average duration seconds | 1954.91 | 2213.03 | heuristic worse |

Conclusion: **baseline won**. The heuristic run found fewer confirmed findings, used more target calls, took longer, and increased the false-positive proxy.

## Consequences

- Do not merge the heuristic routing implementation from `heuristics-ab-experiment`.
- Do not enable hidden hand-written routing heuristics by default.
- Do not add a public CLI flag for this behavior.
- Keep A/B gate hardening as a useful direction, but merge it only through a small separate change if needed.
- Continue to treat weak telemetry and adaptive persona weighting as planning hints only.

## Future rule

Do not reinvest in hand-written strategy-order heuristics unless all of these are true:

1. The experiment uses repeatable benchmark/control conditions.
2. All A/B scope gates pass.
3. Confirmed findings improve or target calls per confirmed finding drops materially.
4. False-positive proxy does not increase.
5. Benign replay does not regress.
6. JudgeAgent and replay gates remain unchanged.

## Alternatives considered

### Merge the full heuristic branch

Rejected. It worsened the measured result and added runtime behavior without proof.

### Keep experimenting immediately

Rejected for now. More runs may be useful later, but this branch should not stay open as an ambiguous pending feature.

### Merge only documentation

Accepted. The durable value is the decision record and future guardrail against repeating the same failed design path.

## Related pages

- [Hide learning complexity from operator](hide-learning-complexity-from-operator.md)
- [Adaptive persona weighting](../research/tool-technology-slice-16-adaptive-persona-weighting.md)
- [Persona weighting report artifacts](../research/tool-technology-slice-17-persona-weighting-report-artifacts.md)
