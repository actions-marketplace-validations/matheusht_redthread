# Current Repo State — RedThread

Date: 2026-08-09  
Current branch: `feat/gepa-phase0-shadow-harness`  
Remote: `origin/main` is ahead of this branch; the GEPA Phase 0–2 work was merged via PR #20 (`58d480f`).

## High-level state

The simplicity product spine is stable:

```text
attack → judge → defend → replay → promotion evidence
```

On top of that stable spine, RedThread is now running the **GEPA research lane**: a reflective prompt-optimizer adoption experiment (arXiv 2507.19457) that is kept strictly under the hood and fully contained. It does not change the default operator path.

## The GEPA research lane

GEPA (Genetic Prompt Optimization / reflective prompt evolution) is being adopted in bounded phases. The lane is additive and research-only:

```text
Phase 0  shadow harness          → containment proven before optimizer exists
Phase 1  prompt-profile adapter  → RedThreadGEPAAdapter + live lift-spike script
Phase 2  Pareto frontier         → per-objective specialist preservation
Phase 3  defense-lane spike      → GEPA over defense architect templates
Phase 4  source-lane spike       → GEPA selects bounded Phase 5 source mutations
```

### Safety contracts (hold in every phase)

- **Allowlist** (`gepa_allowlist.py`): a candidate may only touch
  `pair.system_suffix`, `tap.system_suffix`, `tap.strategies`,
  `crescendo.system_suffix`, `mcts.system_suffix`. Unknown keys are rejected before
  application. Judge, rubrics, golden datasets, promotion logic, defense assets, and
  source files are unreachable by construction.
- **Redaction** (`gepa_side_info.py`): the only channel to a reflection LM is a
  structured, transcript-free payload; canaries, secrets, emails, and banned keys
  are scrubbed, and `assert_clean` fails closed on any leak. Named `gepa_side_info`
  to avoid colliding with telemetry ASI.
- **Control gate** (`gepa_score.py`): the control lane is a fail-closed gate, never a
  reward bonus. Exceeding control limits zeroes the scalar and every Pareto axis.
- **Authority ladder** (`gepa_candidate.py`): `accepted_by_gepa`,
  `accepted_by_redthread_supervisor`, and promotion status stay separate. GEPA-accept
  is a search decision only; it never writes production state.
- **Budget**: live optimization requires explicit `reflection_lm` + positive
  `max_metric_calls`; there is no silent default.
- **Runtime confinement**: snapshots are confined to `autoresearch/runtime/gepa/`
  and never written to production prompt profiles.

### Runtime layout

```text
autoresearch/runtime/gepa/
  candidates/<id>/prompt_profiles.json   (snapshot)
  candidates/<id>/candidate.json         (metadata)
  candidates/<id>/gepa_side_info.json    (redacted side info)
  defense_candidates/                    (Phase 3)
  source_candidates/                     (Phase 4)
  ledger.jsonl                           (append-only evaluation ledger)
  pareto_frontier.json                   (Phase 2 persisted frontier)
```

### Dependency

`gepa==0.1.1` and `litellm>=1.0` are an **optional** extra `[research-gepa]`,
imported lazily. Core installs never require them. Install with:

```bash
pip install 'redthread[research-gepa]'
```

## Merged state on main

`origin/main` (via PR #20, commit `58d480f`) contains GEPA Phase 0, 1, 2:

```text
5f7d791  Phase 0 shadow harness + per-objective plumbing
fbf92f2  Phase 2 Pareto frontier selection
1287866  Phase 1 adapter scaffold (pinned gepa==0.1.1, optional)
db9bc31  Phase 1 live lift-spike script (throwaway) + litellm dep
c04c558  docs: change repo state
```

## Current working tree (uncommitted)

This branch carries uncommitted GEPA Phase 1/3/4 work on top of the merged base:

Tracked modified files:

```text
src/redthread/cli/research/__init__.py    (registers hidden gepa commands)
src/redthread/research/gepa_adapter.py    (propose_new_texts seam)
src/redthread/research/gepa_shadow.py     (train/val/control eval)
src/redthread/research/gepa_side_info.py  (val split in side info)
src/redthread/research/workspace.py       (defense/source candidate dirs, frontier path)
tests/test_gepa_pareto.py
tests/test_gepa_phase0.py
```

Untracked GEPA files:

```text
src/redthread/cli/research/gepa.py                 (hidden: gepa-spike, gepa-defense-spike, gepa-source-spike)
src/redthread/research/gepa_phase1.py              (Phase 1 spike orchestration)
src/redthread/research/gepa_frontier.py            (Phase 2 frontier persistence)
src/redthread/research/gepa_profile_runner.py      (Phase 1 batch runner)
src/redthread/research/gepa_defense_*.py           (Phase 3 defense lane)
src/redthread/research/gepa_source_*.py            (Phase 4 source lane)
tests/test_gepa_phase1.py
tests/test_gepa_defense_phase3.py
tests/test_gepa_source_phase4.py
```

Unrelated untracked items exist in the working tree:

```text
.agent/skills/reddit-authentic-redthread/
docs/UI_GENERATION_STYLE.md
docs/research/phase8_plans/
matheus-v3-ai.pdf
scratch/
src/outreach-extension/
```

Do not include unrelated untracked items in a RedThread core PR unless the user
explicitly asks.

## CLI surface

GEPA research commands are **hidden** (`--help` does not advertise them):

```bash
redthread research gepa-spike \
  --reflection-lm ollama/qwen3 --max-metric-calls 40 \
  --train-slug <slug> --val-slug <slug> --control-slug <slug>

redthread research gepa-defense-spike \
  --reflection-lm ollama/qwen3 --max-metric-calls 40 ...

redthread research gepa-source-spike \
  --reflection-lm ollama/qwen3 --max-metric-calls 40 ...
```

This keeps surfacing under the hood per the prior CEO/CTO review.

## Known compatibility debt (unchanged)

- `DeploymentRecord`
- `defense_deployed`
- `defense_deployments`

Do not remove or rename these without an explicit API-breaking cleanup decision.

## Commands to re-check current state

```bash
git status --short
git branch --show-current
git log -3 --oneline
git diff --stat
python3 scripts/wiki_lint.py
```

## Bottom line

RedThread is in a stable post-simplicity state with a new, fully contained GEPA
research lane running under the hood. The research lane is additive and does not
change the default operator path. Merge and promotion of GEPA artifacts remains
explicit and gated by the RedThread supervisor.
